"""Mô phỏng HÃNG VẬN CHUYỂN GHN / GHTK (cổng 8102).

Mỗi vận đơn tự tiến một trạng thái sau mỗi 3–5 giây cho tới khi giao xong:
    requested → picked_up → in_transit → delivered
Khoảng cách giữa các bước được tính MỘT LẦN lúc tạo vận đơn (ngẫu nhiên tất định theo mã vận đơn) và lưu lại, nên hỏi lịch
sử bao nhiêu lần cũng trả đúng các mốc thời gian cũ (ShipmentDAO bỏ sự kiện trùng theo (kiện, trạng thái, mốc thời gian)).
Quận / huyện nhận có chữ FAIL thì kiện kết thúc `failed` thay vì `delivered`.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from fastapi import Request
from fastapi.responses import HTMLResponse

from common.app import ApiError, create_app

STEP_SECONDS = (3.0, 5.0)
CARRIER = {"standard": ("GHTK", "GHTK"), "express": ("GHN", "GHN")}      # service_level → (carrier, tiền tố mã)

SCHEMA = """
CREATE TABLE IF NOT EXISTS shipments(tracking_no TEXT PRIMARY KEY, carrier TEXT, direction TEXT, service_level TEXT, client_ref TEXT,
                                     from_location TEXT, to_address TEXT, fee INTEGER, created_at TEXT, cancelled INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS events(tracking_no TEXT, seq INTEGER, status TEXT, at TEXT, note TEXT, PRIMARY KEY(tracking_no, seq));
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v INTEGER);
"""


def _reset(store) -> None:
    for t in ("shipments", "events", "meta"):
        store.execute(f"DELETE FROM {t}")


app = create_app("shipping", "Shipping Provider Simulator (GHN / GHTK)", SCHEMA, on_reset=_reset)
store = app.state.store


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat(timespec="seconds")


def _plan(tracking_no: str, start: datetime, to_address: str) -> list[tuple[str, str, str]]:
    rnd = random.Random(tracking_no)                         # tất định theo mã vận đơn
    fail = "FAIL" in (to_address or "").upper()
    steps = [("requested", "Hãng đã nhận yêu cầu"), ("picked_up", "Đã lấy hàng"), ("in_transit", "Đang vận chuyển"),
             ("failed", "Giao hàng thất bại") if fail else ("delivered", "Giao thành công")]
    out, at = [], start
    for i, (status, note) in enumerate(steps):
        if i:
            at += timedelta(seconds=rnd.uniform(*STEP_SECONDS))
        out.append((status, _iso(at), note))
    return out


@app.post("/v1/shipments", status_code=201)
async def create_shipment(request: Request):
    body = await request.json()
    level = body.get("service_level", "standard")
    if level not in CARRIER:
        raise ApiError(422, "invalid_service_level", "service_level phải là standard hoặc express")
    to_address = (body.get("to_address") or "").strip()
    client_ref = str(body.get("client_ref", ""))
    with store.transaction():
        dup = store.one("SELECT tracking_no, carrier FROM shipments WHERE client_ref = ? AND client_ref != '' AND cancelled = 0",
                        (client_ref,))
        if dup:                                              # tạo lại cùng một kiện: trả vận đơn cũ (idempotent)
            return {"carrier": dup["carrier"], "tracking_no": dup["tracking_no"], "duplicate": True}
        carrier, prefix = CARRIER[level]
        row = store.one("SELECT v FROM meta WHERE k = ?", (prefix,))
        n = row["v"] if row else 9000001
        store.execute("INSERT OR REPLACE INTO meta VALUES(?, ?)", (prefix, n + 1))
        tracking_no = f"{prefix}{n:07d}"
        start = datetime.now()
        store.execute("INSERT INTO shipments(tracking_no, carrier, direction, service_level, client_ref, from_location, to_address, fee, created_at) "
                      "VALUES(?,?,?,?,?,?,?,?,?)",
                      (tracking_no, carrier, body.get("direction", "outbound"), level, client_ref, body.get("from_location", ""),
                       to_address, int(body.get("fee") or 0), _iso(start)))
        for seq, (status, at, note) in enumerate(_plan(tracking_no, start, to_address)):
            store.execute("INSERT INTO events VALUES(?,?,?,?,?)", (tracking_no, seq, status, at, note))
    return {"carrier": carrier, "tracking_no": tracking_no}


@app.get("/v1/shipments/{tracking_no}/events")
def events(tracking_no: str):
    ship = store.one("SELECT * FROM shipments WHERE tracking_no = ?", (tracking_no,))
    if ship is None:
        raise ApiError(404, "tracking_not_found", "Không có vận đơn này")
    now = _iso(datetime.now())
    rows = store.query("SELECT status, at AS occurred_at, note FROM events WHERE tracking_no = ? AND at <= ? ORDER BY seq",
                       (tracking_no, now))
    if ship["cancelled"]:
        rows = [r for r in rows if r["status"] == "requested"] + [{"status": "failed", "occurred_at": ship["created_at"],
                                                                   "note": "Đã huỷ"}]
    return {"tracking_no": tracking_no, "carrier": ship["carrier"], "events": rows}


@app.post("/v1/shipments/{tracking_no}/cancel")
def cancel(tracking_no: str):
    ship = store.one("SELECT * FROM shipments WHERE tracking_no = ?", (tracking_no,))
    if ship is None:
        raise ApiError(404, "tracking_not_found")
    picked = store.one("SELECT 1 AS x FROM events WHERE tracking_no = ? AND status = 'picked_up' AND at <= ?",
                       (tracking_no, _iso(datetime.now())))
    if picked:
        raise ApiError(409, "already_picked_up", "Kiện đã được lấy, không huỷ được")
    store.execute("UPDATE shipments SET cancelled = 1 WHERE tracking_no = ?", (tracking_no,))
    return {"tracking_no": tracking_no, "cancelled": True}


@app.get("/board", response_class=HTMLResponse)
def board():
    now = _iso(datetime.now())
    rows = store.query("SELECT s.*, (SELECT status FROM events e WHERE e.tracking_no = s.tracking_no AND e.at <= ? ORDER BY seq DESC LIMIT 1) AS cur "
                       "FROM shipments s ORDER BY s.created_at DESC LIMIT 100", (now,))
    tr = "".join(f"<tr><td>{r['created_at']}</td><td>{r['tracking_no']}</td><td>{r['carrier']}</td><td>{r['direction']}</td>"
                 f"<td>{r['to_address']}</td><td><b>{'cancelled' if r['cancelled'] else r['cur']}</b></td></tr>" for r in rows)
    return ("<meta http-equiv='refresh' content='2'><meta charset='utf-8'><style>body{font:14px Segoe UI}td,th{padding:3px 10px;"
            "border-bottom:1px solid #ddd;text-align:left}</style><h2>Hãng vận chuyển mô phỏng</h2><table><tr><th>Tạo lúc<th>Mã vận đơn"
            f"<th>Hãng<th>Hướng<th>Nơi nhận<th>Trạng thái</tr>{tr}</table>")
