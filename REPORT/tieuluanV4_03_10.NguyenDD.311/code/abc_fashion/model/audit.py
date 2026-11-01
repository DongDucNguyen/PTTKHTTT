# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.audit) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class AuditAction(Enum):
    """<<enumeration>> AuditAction -- layer abc_fashion.model.audit."""
    CREATE = "create"
    UPDATE = "update"
    DEACTIVATE = "deactivate"
    ADJUST_STOCK = "adjust_stock"
    SUSPEND_ACCOUNT = "suspend_account"
    RESET_PASSWORD = "reset_password"


@dataclass(kw_only=True)
class tblAuditLogEntry:
    """<<ORM Persistable>> tblAuditLogEntry -- layer abc_fashion.model.audit."""
    id: int | None = None
    entity: str | None = None
    action: AuditAction | None = None
    changes: str | None = None
    created_at: datetime | None = None
    staffMemberId: int | None = None
