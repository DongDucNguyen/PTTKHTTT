"""Model package fulfilment — Vận chuyển."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from abc_fashion.model.sales import DeliveryService, OrderStatus


class ShipmentDirection(Enum):
    OUTBOUND = "outbound"
    RETURN = "return"


class ShipmentStatus(Enum):
    REQUESTED = "requested"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass(kw_only=True)
class Shipment:
    """Kiện hàng `outbound` (giao) hoặc `return` (lấy về); mỗi kiện rời một kho. DAO gắn động `records`.

    Relationships: ShipmentEvent (composition, 0..*); StockLocation (aggregation, 1);
    ShipmentRecord (aggregation, 1..*); ReturnRequest (aggregation, 0..1).
    """
    id: int | None = None
    direction: ShipmentDirection | None = None
    carrier: str | None = None
    service_level: DeliveryService | None = None
    tracking_no: str | None = None
    fee: int | None = None
    status: ShipmentStatus | None = None
    delivered_at: datetime | None = None
    orderId: int | None = None
    stockLocationId: int | None = None
    returnRequestId: int | None = None


@dataclass(kw_only=True)
class ShipmentEvent:
    """Lịch sử theo dõi của kiện."""
    id: int | None = None
    status: ShipmentStatus | None = None
    occurred_at: datetime | None = None
    note: str | None = None
    shipmentId: int | None = None


@dataclass(kw_only=True)
class ShipmentRecord:
    """Nội dung kiện: dòng đơn + số lượng.

    Relationships: OrderItem (aggregation, 1).
    """
    id: int | None = None
    quantity: int | None = None
    shipmentId: int | None = None
    orderItemId: int | None = None


DISPATCHED = {ShipmentStatus.PICKED_UP, ShipmentStatus.IN_TRANSIT, ShipmentStatus.DELIVERED}


def order_status_from_shipments(shipments: list[Shipment]) -> OrderStatus | None:
    """Trạng thái đơn suy ra từ các kiện `outbound` (mục 9.7); `None` nếu chưa kiện nào đi."""
    out = [s for s in shipments if s.direction == ShipmentDirection.OUTBOUND
           and s.returnRequestId is None and s.status != ShipmentStatus.FAILED]
    if not out:
        return None
    if all(s.status == ShipmentStatus.DELIVERED for s in out):
        return OrderStatus.DELIVERED
    gone = [s for s in out if s.status in DISPATCHED]
    if not gone:
        return None
    return OrderStatus.SHIPPED if len(gone) == len(out) else OrderStatus.PARTIALLY_SHIPPED
