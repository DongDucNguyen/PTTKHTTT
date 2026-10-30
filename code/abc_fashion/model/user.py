"""Model package user — Tài khoản và ba loại người dùng (kèm quy tắc thuần kiểm tra e-mail / điện thoại / mật khẩu)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
PHONE_RE = re.compile(r"^0\d{9,10}$")


def password_problem(pw: str) -> str | None:
    """Lý do mật khẩu chưa đủ mạnh (UC01), `None` nếu hợp lệ."""
    if len(pw) < 8 or not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        return "Mật khẩu ít nhất 8 ký tự, có cả chữ và số"
    return None


class AccountStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class StaffRole(Enum):
    ADMINISTRATOR = "administrator"
    MANAGER = "manager"
    MERCHANDISER = "merchandiser"
    MARKETING = "marketing"
    CUSTOMER_SERVICE = "customer_service"
    WAREHOUSE = "warehouse"
    SALES = "sales"


@dataclass(kw_only=True)
class User:
    """Tài khoản đăng nhập. `email` UNIQUE; `password` lưu hash; `status` active/suspended."""
    id: int | None = None
    email: str | None = None
    password: str | None = None
    status: AccountStatus | None = None
    created_at: datetime | None = None
    last_login_at: datetime | None = None


@dataclass(kw_only=True)
class Customer(User):
    """Khách hàng. `id` là id dòng khách; id tài khoản ở `userId`.

    Relationships: Notification (composition, 0..*).
    """
    id: int | None = None
    full_name: str | None = None
    phone: str | None = None
    marketing_consent: bool | None = None
    preferred_colours: list[str] | None = None
    userId: int | None = None


@dataclass(kw_only=True)
class StaffMember(User):
    """Nhân viên; `code` UNIQUE; `role` quyết định màn hình home.

    Relationships: AuditLogEntry (composition, 0..*).
    """
    id: int | None = None
    code: str | None = None
    full_name: str | None = None
    role: StaffRole | None = None
    userId: int | None = None


@dataclass(kw_only=True)
class Supplier(User):
    """Nhà cung cấp (có thể đăng nhập để xác nhận phiếu nhập)."""
    id: int | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    userId: int | None = None
