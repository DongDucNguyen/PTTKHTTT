# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.user) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class AccountStatus(Enum):
    """<<enumeration>> AccountStatus -- layer abc_fashion.model.user."""
    ACTIVE = "active"
    SUSPENDED = "suspended"


class StaffRole(Enum):
    """<<enumeration>> StaffRole -- layer abc_fashion.model.user."""
    ADMINISTRATOR = "administrator"
    MANAGER = "manager"
    MERCHANDISER = "merchandiser"
    MARKETING = "marketing"
    CUSTOMER_SERVICE = "customer_service"
    WAREHOUSE = "warehouse"
    SALES = "sales"


@dataclass(kw_only=True)
class tblUser:
    """<<ORM Persistable>> tblUser -- layer abc_fashion.model.user."""
    id: int | None = None
    email: str | None = None
    password: str | None = None
    status: AccountStatus | None = None
    created_at: datetime | None = None
    last_login_at: datetime | None = None


@dataclass(kw_only=True)
class tblCustomer(tblUser):
    """<<ORM Persistable>> tblCustomer -- layer abc_fashion.model.user.
    Relationships: tblNotification (composition, 0..*)
    """
    id: int | None = None
    full_name: str | None = None
    phone: str | None = None
    marketing_consent: bool | None = None
    preferred_colours: list[str] | None = None
    userId: int | None = None


@dataclass(kw_only=True)
class tblStaffMember(tblUser):
    """<<ORM Persistable>> tblStaffMember -- layer abc_fashion.model.user.
    Relationships: tblAuditLogEntry (composition, 0..*)
    """
    id: int | None = None
    code: str | None = None
    full_name: str | None = None
    role: StaffRole | None = None
    userId: int | None = None


@dataclass(kw_only=True)
class tblSupplier(tblUser):
    """<<ORM Persistable>> tblSupplier -- layer abc_fashion.model.user."""
    id: int | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    userId: int | None = None
