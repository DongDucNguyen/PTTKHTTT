# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.customer_data) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class Channel(Enum):
    """<<enumeration>> Channel -- layer abc_fashion.model.customer_data."""
    EMAIL = "email"
    SMS = "sms"
    APP = "app"


class LinkedMethodType(Enum):
    """<<enumeration>> LinkedMethodType -- layer abc_fashion.model.customer_data."""
    CARD = "card"
    E_WALLET = "e_wallet"
    BANK_ACCOUNT = "bank_account"


class NotificationEvent(Enum):
    """<<enumeration>> NotificationEvent -- layer abc_fashion.model.customer_data."""
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    RETURN_AUTHORISED = "return_authorised"
    RETURN_REJECTED = "return_rejected"
    REFUND_COMPLETED = "refund_completed"
    EXCHANGE_SHIPPED = "exchange_shipped"


class NotificationStatus(Enum):
    """<<enumeration>> NotificationStatus -- layer abc_fashion.model.customer_data."""
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


@dataclass(kw_only=True)
class tblAddress:
    """<<ORM Persistable>> tblAddress -- layer abc_fashion.model.customer_data."""
    id: int | None = None
    recipient_name: str | None = None
    phone: str | None = None
    street: str | None = None
    ward: str | None = None
    district: str | None = None
    city: str | None = None
    is_default: bool | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class tblNotification:
    """<<ORM Persistable>> tblNotification -- layer abc_fashion.model.customer_data."""
    id: int | None = None
    channel: Channel | None = None
    event_type: NotificationEvent | None = None
    message: str | None = None
    status: NotificationStatus | None = None
    sent_at: datetime | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class tblPaymentMethod:
    """<<ORM Persistable>> tblPaymentMethod -- layer abc_fashion.model.customer_data.
    Relationships: tblCustomer (aggregation, 1)
    """
    id: int | None = None
    provider: str | None = None
    method_type: LinkedMethodType | None = None
    masked_number: str | None = None
    is_default: bool | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class tblSavedSize:
    """<<ORM Persistable>> tblSavedSize -- layer abc_fashion.model.customer_data.
    Relationships: tblCustomer (aggregation, 1); tblCategory (aggregation, 0..*)
    """
    id: int | None = None
    size_label: str | None = None
    customerId: int | None = None
    categoryId: int | None = None
