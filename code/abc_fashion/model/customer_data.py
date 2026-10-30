"""Model package customer_data — Dữ liệu riêng của khách."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    APP = "app"


class LinkedMethodType(Enum):
    CARD = "card"
    E_WALLET = "e_wallet"
    BANK_ACCOUNT = "bank_account"


class NotificationEvent(Enum):
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    RETURN_AUTHORISED = "return_authorised"
    RETURN_REJECTED = "return_rejected"
    REFUND_COMPLETED = "refund_completed"
    EXCHANGE_SHIPPED = "exchange_shipped"


class NotificationStatus(Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


@dataclass(kw_only=True)
class Address:
    """Sổ địa chỉ; một địa chỉ `is_default` cho mỗi khách."""
    id: int | None = None
    recipient_name: str | None = None
    phone: str | None = None
    street: str | None = None
    ward: str | None = None
    district: str | None = None
    city: str | None = None
    is_default: bool | None = None
    customerId: int | None = None

    def one_line(self) -> str:
        return ", ".join(p for p in (self.street, self.ward, self.district, self.city) if p)


@dataclass(kw_only=True)
class Notification:
    """Thông báo đã gửi / chờ gửi cho khách."""
    id: int | None = None
    channel: Channel | None = None
    event_type: NotificationEvent | None = None
    message: str | None = None
    status: NotificationStatus | None = None
    sent_at: datetime | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class PaymentMethod:
    """Phương thức đã liên kết; chỉ `masked_number` (vd. `**** 4242`).

    Relationships: Customer (aggregation, 1).
    """
    id: int | None = None
    provider: str | None = None
    method_type: LinkedMethodType | None = None
    masked_number: str | None = None
    is_default: bool | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class SavedSize:
    """Một cỡ đã lưu cho mỗi (khách, danh mục).

    Relationships: Customer (aggregation, 1); Category (aggregation, 0..*).
    """
    id: int | None = None
    size_label: str | None = None
    customerId: int | None = None
    categoryId: int | None = None
