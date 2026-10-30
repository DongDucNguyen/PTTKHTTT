"""Model package inventory — Kho, tồn kho, sổ kho, nhập hàng."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class MovementReason(Enum):
    SALE = "sale"
    RETURN = "return"
    RESTOCK = "restock"
    ADJUSTMENT = "adjustment"


class RestockStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass(kw_only=True)
class RestockItem:
    """Dòng phiếu nhập (`quantity > 0`).

    Relationships: RestockRequest (aggregation, 1).
    """
    id: int | None = None
    quantity: int | None = None
    restockRequestId: int | None = None
    productVariantId: int | None = None


@dataclass(kw_only=True)
class RestockRequest:
    """Phiếu nhập hàng; `request_no` UNIQUE. DAO gắn động `items`.

    Relationships: Supplier (aggregation, 1); StaffMember (aggregation, 0..1).
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
class StockLevel:
    """Một dòng cho mỗi biến thể. CHECK `0 ≤ reserved ≤ on_hand`, `available = on_hand − reserved`.

    Relationships: StockLocation (aggregation, 0..*).
    """
    id: int | None = None
    on_hand: int | None = None
    reserved: int | None = None
    reorder_point: int | None = None
    available: int | None = None
    productVariantId: int | None = None
    stockLocationId: int | None = None


@dataclass(kw_only=True)
class StockLocation:
    """Kho hàng.

    Relationships: RestockRequest (aggregation, 0..*).
    """
    id: int | None = None
    name: str | None = None
    address: str | None = None


@dataclass(kw_only=True)
class StockMovement:
    """Sổ kho: `quantity_change` (+ nhập / − xuất), `reason`, `reference` (mã đơn, phiếu, trả).

    Relationships: StaffMember (aggregation, 0..1); StockLocation (aggregation, 1).
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


RESTOCK_NEXT: dict[RestockStatus, set[RestockStatus]] = {
    RestockStatus.DRAFT:     {RestockStatus.DRAFT, RestockStatus.SENT, RestockStatus.CANCELLED},
    RestockStatus.SENT:      {RestockStatus.CONFIRMED, RestockStatus.CANCELLED},
    RestockStatus.CONFIRMED: {RestockStatus.RECEIVED},
    RestockStatus.RECEIVED:  set(),
    RestockStatus.CANCELLED: set(),
}


def availability_text(level: StockLevel | None) -> str:
    """Nhãn tồn kho cho trang sản phẩm."""
    if level is None or level.available <= 0:
        return "Hết hàng"
    if level.available <= level.reorder_point:
        return f"Chỉ còn {level.available}"
    return "Còn hàng"
