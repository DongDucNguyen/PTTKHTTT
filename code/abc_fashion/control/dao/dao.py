"""DAO gốc — layer abc_fashion.control.dao. Mở kết nối một lần, dùng chung cho mọi lớp con."""
from __future__ import annotations

import dataclasses
import enum
import functools
import hashlib
import hmac
import os
import secrets
import threading
import typing

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get("ABC_FASHION_DSN",
                     "dbname=abc_fashion_v2 user=postgres host=localhost port=5432")

_local = threading.local()                  # kết nối riêng từng luồng (chế độ web, xem DAO._per_thread)


class DAO:
    """Lớp cha của mọi DAO.

    Mọi đối tượng DAO dùng chung một kết nối (`DAO._shared`) nên một controller có thể bọc nhiều DAO trong
    cùng một transaction: ``with self.order_dao.con.transaction(): ...``. Kết nối ở chế độ autocommit; nhóm
    câu lệnh cần nguyên tử thì bọc trong ``with self.con.transaction():`` (lồng nhau = savepoint).
    Ứng dụng desktop chỉ dùng kết nối ở luồng giao diện. Ứng dụng web phục vụ nhiều request song song nên bật
    `DAO._per_thread`: mỗi luồng một kết nối (transaction không lẫn nhau), đóng ở cuối request.
    """

    _shared: psycopg.Connection | None = None
    _per_thread = False

    def __init__(self):
        self.con = DAO._connect()

    @property
    def con(self) -> psycopg.Connection:
        # tự mở lại nếu kết nối chung đã đóng (mất mạng, server khởi động lại)
        return DAO._connect()

    @con.setter
    def con(self, value) -> None:
        if DAO._per_thread:
            _local.con = value
        else:
            DAO._shared = value

    @staticmethod
    def _connect() -> psycopg.Connection:
        if DAO._per_thread:
            con = getattr(_local, "con", None)
            if con is None or con.closed:
                con = _local.con = psycopg.connect(DSN, autocommit=True, row_factory=dict_row)
            return con
        if DAO._shared is None or DAO._shared.closed:
            DAO._shared = psycopg.connect(DSN, autocommit=True, row_factory=dict_row)
        return DAO._shared

    @staticmethod
    def _release_thread_connection() -> None:
        """Chế độ web: đóng kết nối của luồng hiện tại (cuối mỗi request)."""
        con = getattr(_local, "con", None)
        if con is not None and not con.closed:
            con.close()
        _local.con = None

    @classmethod
    def transaction(cls):
        """Transaction trên kết nối chung, cho Frm cần gộp nhiều DAO (mục 11, quy tắc 3)."""
        return cls._connect().transaction()


class _Abort(Exception):
    """Ném trong khối transaction để rollback có chủ đích (lỗi nghiệp vụ)."""


BUSINESS_ERRORS = (psycopg.errors.UniqueViolation, psycopg.errors.ForeignKeyViolation,
                   psycopg.errors.CheckViolation, psycopg.errors.NotNullViolation)


# ---------- tiện ích dùng chung cho mọi DAO (hàm riêng tư của module) ----------
@functools.cache
def _enum_fields(cls) -> dict[str, type[enum.Enum]]:
    hints = typing.get_type_hints(cls)
    out = {}
    for f in dataclasses.fields(cls):
        for t in (typing.get_args(hints[f.name]) or (hints[f.name],)):
            if isinstance(t, type) and issubclass(t, enum.Enum):
                out[f.name] = t
                break
    return out


@functools.cache
def _field_names(cls) -> frozenset[str]:
    return frozenset(f.name for f in dataclasses.fields(cls))


def _to_entity(cls, row: dict):
    """Tạo entity từ một dòng (dict). Chuỗi → Enum theo type hint.

    Cột không phải trường của lớp (vd. `style_name` từ JOIN) được gắn thành thuộc tính động.
    """
    names, enums = _field_names(cls), _enum_fields(cls)
    kw, extra = {}, {}
    for key, value in row.items():
        if key in names:
            if value is not None and key in enums:
                value = enums[key](value)
            kw[key] = value
        else:
            extra[key] = value
    obj = cls(**kw)
    for key, value in extra.items():
        setattr(obj, key, value)
    return obj


def _val(v):
    """Giá trị để truyền vào câu SQL: Enum -> .value."""
    return v.value if isinstance(v, enum.Enum) else v


def _like(key: str | None) -> str:
    return f"%{(key or '').strip()}%"


def _hash_password(plain: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", plain.encode(), bytes.fromhex(salt), 200_000).hex()
    return f"pbkdf2${salt}${h}"


def _check_password(plain: str, stored: str) -> bool:
    if stored.startswith(("$2a$", "$2b$", "$2y$")):          # bcrypt (dữ liệu tạo từ báo cáo)
        try:
            import bcrypt
            return bcrypt.checkpw(plain.encode(), stored.encode())
        except (ImportError, ValueError):                    # thiếu thư viện hoặc hash hỏng
            return False
    try:
        _, salt, h = stored.split("$")
    except ValueError:                      # dữ liệu mẫu cũ lưu bản rõ
        return hmac.compare_digest(plain.encode(), stored.encode())
    calc = hashlib.pbkdf2_hmac("sha256", plain.encode(), bytes.fromhex(salt), 200_000).hex()
    return hmac.compare_digest(calc, h)


def _is_hashed(stored: str) -> bool:
    return stored.startswith("pbkdf2$")


def _next_no(con: psycopg.Connection, prefix: str, table: str, column: str) -> str:
    """Sinh mã dạng PREFIX-YYMMDD-NNN theo ngày của máy chủ CSDL (mục 13 #13)."""
    day = con.execute("SELECT to_char(now(), 'YYMMDD') AS d").fetchone()["d"]
    stem = f"{prefix}-{day}-"
    row = con.execute(
        f'SELECT coalesce(max(substring("{column}" from %s)::int), 0) + 1 AS n FROM "{table}" '
        f'WHERE "{column}" LIKE %s', (len(stem) + 1, stem + "%")).fetchone()
    return f"{stem}{row['n']:03d}"
