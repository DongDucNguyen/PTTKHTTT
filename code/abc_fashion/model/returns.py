"""Model package returns — Trả / đổi hàng."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from abc_fashion.model.catalogue import MediaType
from abc_fashion.model.sales import OrderItem


class InspectionResult(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class Resolution(Enum):
    REFUND = "refund"
    EXCHANGE = "exchange"


class ReturnReason(Enum):
    TOO_SMALL = "too_small"
    TOO_LARGE = "too_large"
    DEFECT = "defect"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"


class ReturnStatus(Enum):
    REQUESTED = "requested"
    AUTHORISED = "authorised"
    REJECTED = "rejected"
    IN_TRANSIT = "in_transit"
    INSPECTED = "inspected"
    REFUNDED = "refunded"
    EXCHANGED = "exchanged"
    CLOSED = "closed"


class ReturnType(Enum):
    RETURN = "return"
    EXCHANGE = "exchange"


@dataclass(kw_only=True)
class ReturnEvidence:
    """Ảnh / video bằng chứng."""
    id: int | None = None
    url: str | None = None
    media_type: MediaType | None = None
    returnRequestId: int | None = None


@dataclass(kw_only=True)
class ReturnItem(OrderItem):
    """Dòng trả; `orderItemId` trỏ dòng đơn gốc; kết quả kiểm tra.

    `replacementVariantId` là biến thể thay thế khi đổi hàng (bổ sung so với mô hình VP).
    Các trường kế thừa (`unit_price`, `discount`, `sku`, …) được DAO điền từ dòng đơn gốc.
    """
    id: int | None = None
    quantity: int | None = None
    inspection_result: InspectionResult | None = None
    inspection_note: str | None = None
    returnRequestId: int | None = None
    orderItemId: int | None = None
    replacementVariantId: int | None = None


@dataclass(kw_only=True)
class ReturnRequest:
    """Yêu cầu trả / đổi; UNIQUE `orderId`. DAO gắn động `items`, `evidence`, `shipments`.

    Relationships: ReturnEvidence (composition, 0..*); StaffMember (aggregation, 0..1);
    ReturnItem (composition, 1..*).
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


RETURN_WINDOW_DAYS = 30     # giả định, cần ABC Fashion xác nhận

RETURN_NEXT: dict[ReturnStatus, set[ReturnStatus]] = {
    ReturnStatus.REQUESTED:  {ReturnStatus.AUTHORISED, ReturnStatus.REJECTED},
    ReturnStatus.AUTHORISED: {ReturnStatus.IN_TRANSIT},
    ReturnStatus.IN_TRANSIT: {ReturnStatus.INSPECTED},
    ReturnStatus.INSPECTED:  {ReturnStatus.REFUNDED, ReturnStatus.EXCHANGED},
    ReturnStatus.REFUNDED:   {ReturnStatus.CLOSED},
    ReturnStatus.EXCHANGED:  {ReturnStatus.CLOSED},
    ReturnStatus.REJECTED:   {ReturnStatus.CLOSED},
    ReturnStatus.CLOSED:     set(),
}

EVIDENCE_REQUIRED = {ReturnReason.DEFECT, ReturnReason.WRONG_ITEM, ReturnReason.NOT_AS_DESCRIBED}


def within_return_window(delivered_at: datetime | None, now: datetime) -> bool:
    return delivered_at is not None and now <= delivered_at + timedelta(days=RETURN_WINDOW_DAYS)


def refund_line(quantity: int, unit_price: int, line_discount: int, ordered_quantity: int) -> int:
    """Số hoàn của một dòng: `q × unit_price − discount_dòng × q / q_mua` (làm tròn xuống đồng)."""
    return quantity * unit_price - (line_discount or 0) * quantity // ordered_quantity


def refund_amount(items: list[ReturnItem]) -> int:
    """Tổng hoàn cho các dòng `passed` (mỗi dòng cần `ordered_quantity` do DAO gắn)."""
    return sum(refund_line(i.quantity, i.unit_price, i.discount, getattr(i, "ordered_quantity", i.quantity))
               for i in items if i.inspection_result == InspectionResult.PASSED)
