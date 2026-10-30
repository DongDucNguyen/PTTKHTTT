"""SQLite một file cho mỗi dịch vụ: lưu trạng thái bền qua các lần khởi động lại."""
from __future__ import annotations

import sqlite3
import threading


class Store:
    def __init__(self, path: str, schema: str = ""):
        self._con = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._con.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._con.execute("PRAGMA journal_mode=WAL")
        self.script(schema)

    def script(self, sql: str) -> None:
        with self._lock:
            self._con.executescript(sql)

    def execute(self, sql: str, params=()) -> sqlite3.Cursor:
        with self._lock:
            return self._con.execute(sql, params)

    def query(self, sql: str, params=()) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self._con.execute(sql, params).fetchall()]

    def one(self, sql: str, params=()) -> dict | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def transaction(self):
        """`with store.transaction():` — khoá và gói trong BEGIN IMMEDIATE / COMMIT."""
        return _Tx(self)


class _Tx:
    def __init__(self, store: Store):
        self.store = store

    def __enter__(self):
        self.store._lock.acquire()
        self.store._con.execute("BEGIN IMMEDIATE")
        return self.store

    def __exit__(self, exc_type, exc, tb):
        try:
            self.store._con.execute("ROLLBACK" if exc_type else "COMMIT")
        finally:
            self.store._lock.release()
        return False
