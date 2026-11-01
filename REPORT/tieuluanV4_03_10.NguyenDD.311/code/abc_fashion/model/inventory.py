# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.inventory) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class MovementReason(Enum):
    """<<enumeration>> MovementReason -- layer abc_fashion.model.inventory."""
    SALE = "sale"
    RETURN = "return"
    RESTOCK = "restock"
    ADJUSTMENT = "adjustment"


class RestockStatus(Enum):
    """<<enumeration>> RestockStatus -- layer abc_fashion.model.inventory."""
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass(kw_only=True)
class tblRestockItem:
    """<<ORM Persistable>> tblRestockItem -- layer abc_fashion.model.inventory.
    Relationships: tblRestockRequest (aggregation, 1)
    """
    id: int | None = None
    quantity: int | None = None
    restockRequestId: int | None = None
    productVariantId: int | None = None


@dataclass(kw_only=True)
class tblRestockRequest:
    """<<ORM Persistable>> tblRestockRequest -- layer abc_fashion.model.inventory.
    Relationships: tblSupplier (aggregation, 1); tblStaffMember (aggregation, 0..1)
    """
    id: int | None = None
    request_no: str | None = None
    status: RestockStatus | None = None
    created_at: datetime | None = None
    expected_date: date | None = None
    supplier_note: str | None = None
    confirm_at: date | None = None
    supplierId: int | None = None
    stockLocationId: int | None = None
    staffMemberId: int | None = None


@dataclass(kw_only=True)
class tblStockLevel:
    """<<ORM Persistable>> tblStockLevel -- layer abc_fashion.model.inventory.
    Relationships: tblStockLocation (aggregation, 0..*)
    """
    id: int | None = None
    on_hand: int | None = None
    reserved: int | None = None
    reorder_point: int | None = None
    available: int | None = None
    productVariantId: int | None = None
    stockLocationId: int | None = None


@dataclass(kw_only=True)
class tblStockLocation:
    """<<ORM Persistable>> tblStockLocation -- layer abc_fashion.model.inventory.
    Relationships: tblRestockRequest (aggregation, 0..*)
    """
    id: int | None = None
    name: str | None = None
    address: str | None = None


@dataclass(kw_only=True)
class tblStockMovement:
    """<<ORM Persistable>> tblStockMovement -- layer abc_fashion.model.inventory.
    Relationships: tblStaffMember (aggregation, 0..1); tblStockLocation (aggregation, 1)
    """
    id: int | None = None
    quantity_change: int | None = None
    reason: MovementReason | None = None
    reference: str | None = None
    note: str | None = None
    created_at: datetime | None = None
    productVariantId: int | None = None
    stockLocationId: int | None = None
    staffMemberId: int | None = None
