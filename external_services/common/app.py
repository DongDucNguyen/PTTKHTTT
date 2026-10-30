"""Khung FastAPI dùng chung: /health, khoá API, nhật ký yêu cầu, /__admin (điều khiển + quan sát), định dạng lỗi."""
from __future__ import annotations

import json
import time
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from common import config
from common.store import Store

OPEN_PATHS = ("/health", "/docs", "/openapi.json", "/redoc")
OPEN_PREFIXES = ("/board", "/inbox", "/ledger")        # trang HTML xem trạng thái, để trình diễn


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str = ""):
        self.status, self.code, self.message = status, code, message


def error_body(code: str, message: str = "") -> dict:
    return {"error": {"code": code, "message": message or code}}


def create_app(name: str, title: str, schema: str = "", on_reset: Callable[[Store], None] | None = None,
               extra_health: Callable[[], dict] | None = None) -> FastAPI:
    app = FastAPI(title=title, version="1.0")
    store = Store(config.db_path(name), schema + """
        CREATE TABLE IF NOT EXISTS _calls(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, method TEXT, path TEXT,
                                          status INTEGER, ms INTEGER, body TEXT);
        CREATE TABLE IF NOT EXISTS _behavior(k TEXT PRIMARY KEY, v TEXT);""")
    app.state.store, app.state.name = store, name
    key = config.api_key(name)

    def behavior() -> dict:
        return {r["k"]: json.loads(r["v"]) for r in store.query("SELECT k, v FROM _behavior")}

    @app.exception_handler(ApiError)
    async def _api_error(_: Request, e: ApiError):
        return JSONResponse(error_body(e.code, e.message), status_code=e.status)

    @app.middleware("http")
    async def _guard(request: Request, call_next):
        started, path = time.time(), request.url.path
        is_api = path.startswith("/v1") or path.startswith("/__admin")
        body = (await request.body())[:2000] if is_api and request.headers.get("content-type", "").startswith("application/json") else b""
        response = None
        if is_api and request.headers.get("authorization") != f"Bearer {key}":
            response = JSONResponse(error_body("unauthorized", "Thiếu hoặc sai khoá API"), status_code=401)
        elif path.startswith("/v1"):
            b = behavior()                                  # gây lỗi / trễ có chủ đích
            if b.get("latency_ms"):
                time.sleep(b["latency_ms"] / 1000)
            if b.get("fail_next", 0) > 0:
                store.execute("INSERT OR REPLACE INTO _behavior VALUES('fail_next', ?)", (json.dumps(b["fail_next"] - 1),))
                response = JSONResponse(error_body("injected_failure", "Lỗi được gây có chủ đích"),
                                        status_code=int(b.get("status", 503)))
        if response is None:
            response = await call_next(request)
        if is_api and not path.startswith("/__admin/calls"):
            store.execute("INSERT INTO _calls(ts, method, path, status, ms, body) VALUES(?,?,?,?,?,?)",
                          (started, request.method, path + (("?" + request.url.query) if request.url.query else ""),
                           response.status_code, int((time.time() - started) * 1000), body.decode("utf-8", "replace")))
        return response

    @app.get("/health")
    def health():
        return {"status": "ok", "service": name, "title": title, **(extra_health() if extra_health else {})}

    @app.get("/__admin/calls")
    def calls(limit: int = 50, path_contains: str = ""):
        rows = store.query("SELECT * FROM _calls WHERE path LIKE ? ORDER BY id DESC LIMIT ?", (f"%{path_contains}%", limit))
        return {"calls": rows}

    @app.post("/__admin/behavior")
    async def set_behavior(request: Request):
        data = await request.json()                          # {"fail_next": 2, "status": 503, "latency_ms": 3000}
        for k, v in data.items():
            store.execute("INSERT OR REPLACE INTO _behavior VALUES(?, ?)", (k, json.dumps(v)))
        return {"behavior": behavior()}

    @app.post("/__admin/reset")
    def reset():
        store.execute("DELETE FROM _calls")
        store.execute("DELETE FROM _behavior")
        if on_reset:
            on_reset(store)
        return {"status": "reset"}

    return app
