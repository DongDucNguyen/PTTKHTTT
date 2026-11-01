# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.sales) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from abc_fashion.model.catalogue import tblProductVariant


class DeliveryService(Enum):
    """<<enumeration>> DeliveryService -- layer abc_fashion.model.sales."""
    STANDARD = "standard"
    EXPRESS = "express"


class DiscountType(Enum):
    """<<enumeration>> DiscountType -- layer abc_fashion.model.sales."""
    PERCENT = "percent"
    FIXED_AMOUNT = "fixed_amount"


class OrderStatus(Enum):
    """<<enumeration>> OrderStatus -- layer abc_fashion.model.sales."""
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PARTIALLY_SHIPPED = "partially_shipped"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentKind(Enum):
    """<<enumeration>> PaymentKind -- layer abc_fashion.model.sales."""
    CHARGE = "charge"
    REFUND = "refund"


class PaymentMethodType(Enum):
    """<<enumeration>> PaymentMethodType -- layer abc_fashion.model.sales."""
    COD = "cod"
    CARD = "card"
    E_WALLET = "e_wallet"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(Enum):
    """<<enumeration>> PaymentStatus -- layer abc_fashion.model.sales."""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PromoType(Enum):
    """<<enumeration>> PromoType -- layer abc_fashion.model.sales."""
    SEASONAL = "seasonal"
    FLASH_SALE = "flash_sale"
    CLEARANCE = "clearance"
    LOYALTY = "loyalty"


class PromotionStatus(Enum):
    """<<enumeration>> PromotionStatus -- layer abc_fashion.model.sales."""
    DRAFT = "draft"
    ACTIVE = "active"
    ENDED = "ended"


@dataclass(kw_only=True)
class tblCart:
    """<<ORM Persistable>> tblCart -- layer abc_fashion.model.sales.
    Relationships: tblCustomer (aggregation, 1)
    """
    id: int | None = None
    updated_at: datetime | None = None
    subtotal: int | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class tblCartItem(tblProductVariant):
    """<<ORM Persistable>> tblCartItem -- layer abc_fashion.model.sales.
    Relationships: tblCart (aggregation, 1)
    """
    id: int | None = None
    quantity: int | None = None
    added_at: datetime | None = None
    cartId: int | None = None
    productVariantId: int | None = None


@dataclass(kw_only=True)
class tblOrder:
    """<<ORM Persistable>> tblOrder -- layer abc_fashion.model.sales.
    Relationships: tblOrderItem (composition, 1..*); tblCustomer (aggregation, 1); tblPayment (composition, 0..*); tblShipment (composition, 0..*); tblReturnRequest (composition, 0..1)
    """
    id: int | None = None
    order_no: str | None = None
    status: OrderStatus | None = None
    placed_at: datetime | None = None
    subtotal: int | None = None
    discount: int | None = None
    shipping_fee: int | None = None
    grand_total: int | None = None
    delivery_service: DeliveryService | None = None
    note: str | None = None
    cancel_reason: str | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class tblOrderItem(tblCartItem):
    """<<ORM Persistable>> tblOrderItem -- layer abc_fashion.model.sales.
    Relationships: tblReview (composition, 0..1)
    """
    id: int | None = None
    quantity: int | None = None
    unit_price: int | None = None
    discount: int | None = None
    line_total: int | None = None
    orderId: int | None = None
    productVariantId: int | None = None


@dataclass(kw_only=True)
class tblOrderVoucher:
    """tblOrderVoucher -- layer abc_fashion.model.sales.
    Relationships: tblVoucher (aggregation, Unspecified); tblOrder (aggregation, Unspecified)
    """
    id: int | None = None
    orderId: int | None = None
    voucherId: int | None = None


@dataclass(kw_only=True)
class tblPayment:
    """<<ORM Persistable>> tblPayment -- layer abc_fashion.model.sales.
    Relationships: tblPaymentMethod (aggregation, 1)
    """
    id: int | None = None
    kind: PaymentKind | None = None
    method: PaymentMethodType | None = None
    amount: int | None = None
    status: PaymentStatus | None = None
    transaction_ref: str | None = None
    created_at: datetime | None = None
    orderId: int | None = None
    paymentMethodId: int | None = None


@dataclass(kw_only=True)
class tblPromotion:
    """<<ORM Persistable>> tblPromotion -- layer abc_fashion.model.sales.
    Relationships: tblVoucher (composition, 0..*)
    """
    id: int | None = None
    name: str | None = None
    promo_type: PromoType | None = None
    discount_type: DiscountType | None = None
    discount_value: int | None = None
    min_order_value: int | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: PromotionStatus | None = None


@dataclass(kw_only=True)
class tblPromotionStyle:
    """tblPromotionStyle -- layer abc_fashion.model.sales.
    Relationships: tblPromotion (aggregation, Unspecified); tblStyle (aggregation, Unspecified)
    """
    id: int | None = None
    promotionId: int | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class tblVoucher:
    """<<ORM Persistable>> tblVoucher -- layer abc_fashion.model.sales."""
    id: int | None = None
    code: str | None = None
    usage_limit: int | None = None
    used_count: int | None = None
    promotionId: int | None = None
