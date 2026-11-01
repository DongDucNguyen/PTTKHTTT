# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.returns) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from abc_fashion.model.catalogue import MediaType
from abc_fashion.model.sales import tblOrderItem


class InspectionResult(Enum):
    """<<enumeration>> InspectionResult -- layer abc_fashion.model.returns."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class Resolution(Enum):
    """<<enumeration>> Resolution -- layer abc_fashion.model.returns."""
    REFUND = "refund"
    EXCHANGE = "exchange"


class ReturnReason(Enum):
    """<<enumeration>> ReturnReason -- layer abc_fashion.model.returns."""
    TOO_SMALL = "too_small"
    TOO_LARGE = "too_large"
    DEFECT = "defect"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"


class ReturnStatus(Enum):
    """<<enumeration>> ReturnStatus -- layer abc_fashion.model.returns."""
    REQUESTED = "requested"
    AUTHORISED = "authorised"
    REJECTED = "rejected"
    IN_TRANSIT = "in_transit"
    INSPECTED = "inspected"
    REFUNDED = "refunded"
    EXCHANGED = "exchanged"
    CLOSED = "closed"


class ReturnType(Enum):
    """<<enumeration>> ReturnType -- layer abc_fashion.model.returns."""
    RETURN = "return"
    EXCHANGE = "exchange"


@dataclass(kw_only=True)
class tblReturnEvidence:
    """<<ORM Persistable>> tblReturnEvidence -- layer abc_fashion.model.returns."""
    id: int | None = None
    url: str | None = None
    media_type: MediaType | None = None
    returnRequestId: int | None = None


@dataclass(kw_only=True)
class tblReturnItem(tblOrderItem):
    """<<ORM Persistable>> tblReturnItem -- layer abc_fashion.model.returns."""
    id: int | None = None
    quantity: int | None = None
    inspection_result: InspectionResult | None = None
    inspection_note: str | None = None
    returnRequestId: int | None = None
    orderItemId: int | None = None


@dataclass(kw_only=True)
class tblReturnRequest:
    """<<ORM Persistable>> tblReturnRequest -- layer abc_fashion.model.returns.
    Relationships: tblReturnEvidence (composition, 0..*); tblStaffMember (aggregation, 0..1); tblReturnItem (composition, 1..*)
    """
    id: int | None = None
    return_no: str | None = None
    return_type: ReturnType | None = None
    reason_code: ReturnReason | None = None
    reason_detail: str | None = None
    desired_resolution: Resolution | None = None
    status: ReturnStatus | None = None
    requested_at: datetime | None = None
    decided_at: datetime | None = None
    decision_note: str | None = None
    orderId: int | None = None
    staffMemberId: int | None = None
