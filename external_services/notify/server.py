"""Mô phỏng DỊCH VỤ E-MAIL / SMS (cổng 8103): nhận thư, lưu lại, cho xem ở /inbox.

Người nhận không hợp lệ (trả 422 → gateway trả False → Notification.status = failed):
  - e-mail kết thúc `@bounce.test` hoặc không có dấu @;
  - số điện thoại kết thúc `0000` hoặc ít hơn 9 chữ số.
"""
from __future__ import annotations

import html
import re
from datetime import datetime

from fastapi import Request
from fastapi.responses import HTMLResponse

from common.app import ApiError, create_app

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, channel TEXT, recipient TEXT,
                                    event_type TEXT, body TEXT, client_ref TEXT, status TEXT);
"""

app = create_app("notify", "Email/SMS Service Simulator", SCHEMA, on_reset=lambda s: s.execute("DELETE FROM messages"))
store = app.state.store


def _valid(channel: str, to: str) -> str | None:
    to = (to or "").strip()
    if channel == "email":
        if "@" not in to or to.lower().endswith("@bounce.test"):
            return "Địa chỉ e-mail không hợp lệ"
    elif channel == "sms":
        digits = re.sub(r"\D", "", to)
        if len(digits) < 9 or digits.endswith("0000"):
            return "Số điện thoại không hợp lệ"
    elif channel != "app":
        return "channel phải là email / sms / app"
    return None


@app.post("/v1/messages", status_code=202)
async def send(request: Request):
    body = await request.json()
    channel, to = body.get("channel", "email"), body.get("to", "")
    problem = _valid(channel, to)
    if problem:
        raise ApiError(422, "invalid_recipient", problem)
    cur = store.execute("INSERT INTO messages(created_at, channel, recipient, event_type, body, client_ref, status) VALUES(?,?,?,?,?,?,'delivered')",
                        (datetime.now().isoformat(timespec="seconds"), channel, to, body.get("event_type", ""),
                         body.get("body", ""), str(body.get("client_ref", ""))))
    return {"id": cur.lastrowid, "status": "delivered"}


@app.get("/v1/messages")
def messages(to: str = "", event_type: str = "", limit: int = 100):
    return {"messages": store.query("SELECT * FROM messages WHERE recipient LIKE ? AND event_type LIKE ? ORDER BY id DESC LIMIT ?",
                                    (f"%{to}%", f"%{event_type}%", limit))}


@app.get("/inbox", response_class=HTMLResponse)
def inbox(to: str = ""):
    rows = store.query("SELECT * FROM messages WHERE recipient LIKE ? ORDER BY id DESC LIMIT 100", (f"%{to}%",))
    tr = "".join(f"<tr><td>{r['created_at']}</td><td>{r['channel']}</td><td>{html.escape(r['recipient'])}</td><td>{r['event_type']}</td>"
                 f"<td>{html.escape(r['body'])}</td></tr>" for r in rows)
    return ("<meta http-equiv='refresh' content='3'><meta charset='utf-8'><style>body{font:14px Segoe UI}td,th{padding:3px 10px;"
            "border-bottom:1px solid #ddd;text-align:left}</style><h2>Hộp thư mô phỏng</h2><table><tr><th>Lúc<th>Kênh<th>Người nhận"
            f"<th>Sự kiện<th>Nội dung</tr>{tr}</table>")
