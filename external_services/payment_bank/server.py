"""Mô phỏng NGÂN HÀNG / cổng thanh toán (cổng 8101). Đơn giản có chủ đích: đủ số dư và đủ điều kiện thì qua.

Điều kiện một giao dịch thu tiền thẻ / ví đã liên kết:
  1. số tiền > 0 và ≤ hạn mức một giao dịch (100.000.000 đ);
  2. tài khoản (xác định bằng 4 số cuối) không bị khoá;
  3. số dư ≥ số tiền.
Tài khoản chưa từng thấy được mở tự động với số dư mặc định 50.000.000 đ. COD / chuyển khoản / ví chưa liên kết
(không có tài khoản) chỉ cần điều kiện 1.
Tài khoản mẫu: 4242 (100 triệu), 0002 (bị khoá — thử UC08 E2), 9995 (chỉ 100.000 đ — thử không đủ số dư).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import Header, Request
from fastapi.responses import HTMLResponse

from common.app import ApiError, create_app

MAX_PER_TRANSACTION = 100_000_000
DEFAULT_BALANCE = 50_000_000
SEED = {"4242": ("active", 100_000_000), "0002": ("blocked", 0), "9995": ("active", 100_000)}

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts(last4 TEXT PRIMARY KEY, kind TEXT, provider TEXT, status TEXT, balance INTEGER, created_at TEXT);
CREATE TABLE IF NOT EXISTS transactions(ref TEXT PRIMARY KEY, kind TEXT, order_no TEXT, amount INTEGER, method TEXT, last4 TEXT,
                                        status TEXT, reason TEXT, parent_ref TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS idempotency(key TEXT PRIMARY KEY, response TEXT);
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v INTEGER);
"""


def _seed(store) -> None:
    for last4, (status, balance) in SEED.items():
        store.execute("INSERT OR REPLACE INTO accounts VALUES(?, 'card', 'Seed', ?, ?, ?)",
                      (last4, status, balance, _now()))


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _reset(store) -> None:
    for t in ("accounts", "transactions", "idempotency", "meta"):
        store.execute(f"DELETE FROM {t}")
    _seed(store)


app = create_app("payment", "Bank / Payment Simulator", SCHEMA, on_reset=_reset)
store = app.state.store
if not store.one("SELECT 1 AS x FROM accounts LIMIT 1"):
    _seed(store)


def _record(kind, order_no, amount, method, last4, status, reason="", parent=None) -> dict:
    ref = ("BANK-R-" if kind == "refund" else "BANK-") + uuid.uuid4().hex[:12].upper()
    store.execute("INSERT INTO transactions VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (ref, kind, order_no, amount, method, last4, status, reason, parent, _now()))
    return {"transaction_ref": ref, "status": status, "reason": reason, "amount": amount}


def _idempotent(key: str | None, produce):
    if key:
        hit = store.one("SELECT response FROM idempotency WHERE key = ?", (key,))
        if hit:
            import json
            return json.loads(hit["response"])
    result = produce()
    if key:
        import json
        store.execute("INSERT OR REPLACE INTO idempotency VALUES(?, ?)", (key, json.dumps(result)))
    return result


@app.post("/v1/accounts")
async def link_account(request: Request):
    """Liên kết thẻ / ví / tài khoản: mở tài khoản mới, trả 4 số cuối (không bao giờ nhận hay lưu số thẻ đầy đủ)."""
    body = await request.json()
    kind, provider = body.get("type", "card"), body.get("provider", "")
    if kind not in ("card", "e_wallet", "bank_account"):
        raise ApiError(422, "invalid_type", "type phải là card / e_wallet / bank_account")
    with store.transaction():
        row = store.one("SELECT v FROM meta WHERE k = 'next_last4'")
        n = row["v"] if row else 7000
        while store.one("SELECT 1 AS x FROM accounts WHERE last4 = ?", (f"{n:04d}",)):
            n += 1
        store.execute("INSERT OR REPLACE INTO meta VALUES('next_last4', ?)", (n + 1,))
        last4 = f"{n:04d}"
        store.execute("INSERT INTO accounts VALUES(?,?,?, 'active', ?, ?)", (last4, kind, provider, DEFAULT_BALANCE, _now()))
    return {"last4": last4, "masked_number": f"**** {last4}", "type": kind, "provider": provider}


@app.post("/v1/charges")
async def charge(request: Request, idempotency_key: str | None = Header(default=None)):
    body = await request.json()
    amount, last4, order_no = body.get("amount"), (body.get("last4") or "").strip() or None, body.get("order_no", "")
    method = body.get("method", "card")
    if not isinstance(amount, int) or amount <= 0:
        raise ApiError(422, "invalid_amount", "amount phải là số nguyên dương (VND)")

    def produce() -> dict:
        with store.transaction():
            if amount > MAX_PER_TRANSACTION:
                return _record("charge", order_no, amount, method, last4, "declined", "amount_too_large")
            if last4 is None:                                   # COD / chuyển khoản / ví chưa liên kết
                return _record("charge", order_no, amount, method, None, "succeeded")
            acc = store.one("SELECT * FROM accounts WHERE last4 = ?", (last4,))
            if acc is None:                                     # tài khoản lạ: tự mở với số dư mặc định
                store.execute("INSERT INTO accounts VALUES(?, 'card', '', 'active', ?, ?)", (last4, DEFAULT_BALANCE, _now()))
                acc = store.one("SELECT * FROM accounts WHERE last4 = ?", (last4,))
            if acc["status"] != "active":
                return _record("charge", order_no, amount, method, last4, "declined", "account_blocked")
            if acc["balance"] < amount:
                return _record("charge", order_no, amount, method, last4, "declined", "insufficient_funds")
            store.execute("UPDATE accounts SET balance = balance - ? WHERE last4 = ?", (amount, last4))
            return _record("charge", order_no, amount, method, last4, "succeeded")
    return _idempotent(idempotency_key, produce)


@app.post("/v1/refunds")
async def refund(request: Request, idempotency_key: str | None = Header(default=None)):
    body = await request.json()
    parent_ref, amount = body.get("transaction_ref"), body.get("amount")
    if not isinstance(amount, int) or amount <= 0:
        raise ApiError(422, "invalid_amount", "amount phải là số nguyên dương (VND)")

    def produce() -> dict:
        with store.transaction():
            parent = store.one("SELECT * FROM transactions WHERE ref = ? AND kind = 'charge'", (parent_ref,))
            if parent is None:                       # COD / dữ liệu cũ: ngân hàng không có giao dịch thu để đối chiếu
                return _record("refund", "", amount, "unverified", None, "succeeded", "unverified_charge", parent_ref)
            if parent["status"] != "succeeded":
                return _record("refund", parent["order_no"], amount, parent["method"], parent["last4"], "declined",
                               "charge_not_succeeded", parent_ref)
            done = store.one("SELECT coalesce(sum(amount), 0) AS s FROM transactions WHERE parent_ref = ? AND kind = 'refund' "
                             "AND status = 'succeeded'", (parent_ref,))["s"]
            if amount > parent["amount"] - done:
                return _record("refund", parent["order_no"], amount, parent["method"], parent["last4"], "declined",
                               "exceeds_refundable", parent_ref)
            if parent["last4"]:
                store.execute("UPDATE accounts SET balance = balance + ? WHERE last4 = ?", (amount, parent["last4"]))
            return _record("refund", parent["order_no"], amount, parent["method"], parent["last4"], "succeeded", "", parent_ref)
    return _idempotent(idempotency_key, produce)


@app.get("/v1/transactions")
def transactions(reference: str = "", limit: int = 100):
    rows = store.query("SELECT * FROM transactions WHERE order_no LIKE ? ORDER BY created_at DESC, rowid DESC LIMIT ?",
                       (f"%{reference}%", limit))
    return {"transactions": rows}


@app.get("/v1/accounts/{last4}")
def account(last4: str):
    acc = store.one("SELECT * FROM accounts WHERE last4 = ?", (last4,))
    if acc is None:
        raise ApiError(404, "account_not_found")
    return acc


@app.put("/__admin/accounts/{last4}")
async def admin_account(last4: str, request: Request):
    data = await request.json()                                  # {"balance": 1000, "status": "blocked"}
    store.execute("INSERT OR IGNORE INTO accounts VALUES(?, 'card', '', 'active', ?, ?)", (last4, DEFAULT_BALANCE, _now()))
    for field in ("balance", "status"):
        if field in data:
            store.execute(f"UPDATE accounts SET {field} = ? WHERE last4 = ?", (data[field], last4))
    return store.one("SELECT * FROM accounts WHERE last4 = ?", (last4,))


@app.get("/ledger", response_class=HTMLResponse)
def ledger():
    rows = store.query("SELECT * FROM transactions ORDER BY created_at DESC, rowid DESC LIMIT 100")
    accs = store.query("SELECT * FROM accounts ORDER BY last4")
    tr = "".join(f"<tr><td>{r['created_at']}</td><td>{r['kind']}</td><td>{r['order_no']}</td><td>{r['amount']:,}</td>"
                 f"<td>{r['method']}</td><td>{r['last4'] or ''}</td><td>{r['status']}</td><td>{r['reason']}</td><td>{r['ref']}</td></tr>"
                 for r in rows)
    ar = "".join(f"<tr><td>{a['last4']}</td><td>{a['provider']}</td><td>{a['status']}</td><td>{a['balance']:,}</td></tr>" for a in accs)
    return (f"<meta http-equiv='refresh' content='3'><meta charset='utf-8'><style>body{{font:14px Segoe UI}}td,th{{padding:3px 10px;"
            f"border-bottom:1px solid #ddd;text-align:left}}</style><h2>Ngân hàng mô phỏng</h2><h3>Tài khoản</h3><table><tr><th>4 số cuối"
            f"<th>NCC<th>Trạng thái<th>Số dư</tr>{ar}</table><h3>Giao dịch</h3><table><tr><th>Thời điểm<th>Loại<th>Đơn<th>Số tiền"
            f"<th>PT<th>Thẻ<th>KQ<th>Lý do<th>Mã</tr>{tr}</table>")
