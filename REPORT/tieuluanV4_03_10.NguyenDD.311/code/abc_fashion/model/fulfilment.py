# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.fulfilment) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from abc_fashion.model.sales import DeliveryService


class ShipmentDirection(Enum):
    """<<enumeration>> ShipmentDirection -- layer abc_fashion.model.fulfilment."""
    OUTBOUND = "outbound"
    RETURN = "return"


class ShipmentStatus(Enum):
    """<<enumeration>> ShipmentStatus -- layer abc_fashion.model.fulfilment."""
    REQUESTED = "requested"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass(kw_only=True)
class tblShipment:
    """<<ORM Persistable>> tblShipment -- layer abc_fashion.model.fulfilment.
    Relationships: tblShipmentEvent (composition, 0..*); tblStockLocation (aggregation, 1); tblShipmentRecord (aggregation, 1..*); tblReturnRequest (aggregation, 0..1)
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
class tblShipmentEvent:
    """<<ORM Persistable>> tblShipmentEvent -- layer abc_fashion.model.fulfilment."""
    id: int | None = None
    status: ShipmentStatus | None = None
    occurred_at: datetime | None = None
    note: str | None = None
    shipmentId: int | None = None


@dataclass(kw_only=True)
class tblShipmentRecord:
    """<<ORM Persistable>> tblShipmentRecord -- layer abc_fashion.model.fulfilment.
    Relationships: tblOrderItem (aggregation, 1)
    """
    id: int | None = None
    quantity: int | None = None
    shipmentId: int | None = None
    orderItemId: int | None = None
