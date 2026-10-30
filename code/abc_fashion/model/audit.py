"""Model package audit — Nhật ký."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AuditAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    DEACTIVATE = "deactivate"
    ADJUST_STOCK = "adjust_stock"
    SUSPEND_ACCOUNT = "suspend_account"
    RESET_PASSWORD = "reset_password"


@dataclass(kw_only=True)
class AuditLogEntry:
    """Mỗi thay đổi quan trọng của nhân viên."""
    id: int | None = None
    entity: str | None = None
    action: AuditAction | None = None
    changes: str | None = None
    created_at: datetime | None = None
    staffMemberId: int | None = None
