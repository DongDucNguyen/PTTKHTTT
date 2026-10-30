"""Model package sales — Giỏ hàng, khuyến mãi, đơn hàng, thanh toán.

Ngoài entity, module chứa các quy tắc thuần của dữ liệu bán hàng (máy trạng thái đơn, tính tiền,
phân bổ giảm giá, kiểm tra voucher) để kiểm thử được mà không cần CSDL hay giao diện.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from abc_fashion.model.catalogue import ProductVariant


class DeliveryService(Enum):
    STANDARD = "standard"
    EXPRESS = "express"


class DiscountType(Enum):
    PERCENT = "percent"
    FIXED_AMOUNT = "fixed_amount"


class OrderStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PARTIALLY_SHIPPED = "partially_shipped"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentKind(Enum):
    CHARGE = "charge"
    REFUND = "refund"


class PaymentMethodType(Enum):
    COD = "cod"
    CARD = "card"
    E_WALLET = "e_wallet"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PromoType(Enum):
    SEASONAL = "seasonal"
    FLASH_SALE = "flash_sale"
    CLEARANCE = "clearance"
    LOYALTY = "loyalty"


class PromotionStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ENDED = "ended"


@dataclass(kw_only=True)
class Cart:
    """Một giỏ / khách (UNIQUE `customerId`). DAO gắn động `cart.items`.

    Relationships: Customer (aggregation, 1).
    """
    id: int | None = None
    updated_at: datetime | None = None
    subtotal: int | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class CartItem(ProductVariant):
    """Dòng giỏ — "là" một biến thể với số lượng. `quantity > 0`.

    Relationships: Cart (aggregation, 1).
    """
    id: int | None = None
    quantity: int | None = None
    added_at: datetime | None = None
    cartId: int | None = None
    productVariantId: int | None = None


@dataclass(kw_only=True)
class Order:
    """Đơn hàng; `order_no` UNIQUE; CHECK `grand_total = subtotal − discount + shipping_fee`.

    `ship_*` chụp địa chỉ giao hàng lúc đặt (mục 13 #4). DAO gắn động `items`, `payments`,
    `shipments`, `vouchers`.

    Relationships: OrderItem (composition, 1..*); Customer (aggregation, 1);
    Payment (composition, 0..*); Shipment (composition, 0..*); ReturnRequest (composition, 0..1).
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
    ship_recipient: str | None = None
    ship_phone: str | None = None
    ship_address: str | None = None
    customerId: int | None = None


@dataclass(kw_only=True)
class OrderItem(CartItem):
    """Dòng đơn: `unit_price`, `discount` đóng băng lúc đặt; CHECK `line_total = quantity × unit_price − discount`.

    Relationships: Review (composition, 0..1).
    """
    id: int | None = None
    quantity: int | None = None
    unit_price: int | None = None
    discount: int | None = None
    line_total: int | None = None
    orderId: int | None = None
    productVariantId: int | None = None


@dataclass(kw_only=True)
class OrderVoucher:
    """Bảng nối Order M:N Voucher.

    Relationships: Voucher (aggregation); Order (aggregation).
    """
    id: int | None = None
    orderId: int | None = None
    voucherId: int | None = None


@dataclass(kw_only=True)
class Payment:
    """Lần thu (`charge`) / hoàn (`refund`); `transaction_ref` của cổng thanh toán.

    Relationships: PaymentMethod (aggregation, 0..1).
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
class Promotion:
    """Chương trình; CHECK `ends_at > starts_at`; giảm % trong 1–100. DAO gắn động `styles`, `vouchers`.

    Relationships: Voucher (composition, 0..*).
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
class PromotionStyle:
    """Bảng nối Promotion M:N Style."""
    id: int | None = None
    promotionId: int | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class Voucher:
    """Mã giảm giá; `code` UNIQUE; CHECK `0 ≤ used_count ≤ usage_limit`."""
    id: int | None = None
    code: str | None = None
    usage_limit: int | None = None
    used_count: int | None = None
    promotionId: int | None = None


# ====================================================================== quy tắc thuần

ORDER_NEXT: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING_PAYMENT:   {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED:         {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING:        {OrderStatus.PARTIALLY_SHIPPED, OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.PARTIALLY_SHIPPED: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED:           {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED:         {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}

ORDER_CANCELLABLE = {OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED, OrderStatus.PROCESSING}

SHIPPING_FEE = {DeliveryService.STANDARD: 30_000, DeliveryService.EXPRESS: 50_000}
FREE_SHIPPING_THRESHOLD = 500_000
PENDING_PAYMENT_TIMEOUT_MINUTES = 30


def can_transition(old: OrderStatus, new: OrderStatus) -> bool:
    return new in ORDER_NEXT.get(old, set())


def shipping_fee(service: DeliveryService, amount_after_discount: int) -> int:
    """Phí vận chuyển (UC30): miễn phí khi `subtotal − discount ≥ FREE_SHIPPING_THRESHOLD`."""
    if amount_after_discount >= FREE_SHIPPING_THRESHOLD:
        return 0
    return SHIPPING_FEE[service or DeliveryService.STANDARD]


def promotion_amount(promotion: Promotion, base: int) -> int:
    """Số tiền giảm của chương trình trên một khoản `base` (không vượt `base`)."""
    if not promotion or base <= 0:
        return 0
    if promotion.discount_type == DiscountType.PERCENT:
        return base * promotion.discount_value // 100
    return min(promotion.discount_value, base)


def promo_price(price: int, promotion: Promotion | None) -> int:
    """Giá một đơn vị sau khuyến mãi tự động (chương trình không có voucher)."""
    if promotion is None:
        return price
    return price - promotion_amount(promotion, price)


def is_running(promotion: Promotion, now: datetime) -> bool:
    return (promotion.status == PromotionStatus.ACTIVE
            and promotion.starts_at <= now < promotion.ends_at)


def apply_discount(items: list[OrderItem], eligible_style_ids: set[int], amount: int) -> int:
    """Phân bổ `amount` vào `discount` của các dòng đủ điều kiện theo tỉ lệ thành tiền.

    Dòng cuối nhận phần dư để tổng khớp đến từng đồng. Trả số tiền thực giảm (≤ tổng đủ điều kiện).
    """
    elig = [i for i in items if i.styleId in eligible_style_ids]
    base = sum(i.quantity * i.unit_price - (i.discount or 0) for i in elig)
    amount = max(0, min(amount, base))
    left = amount
    for k, i in enumerate(elig):
        line_base = i.quantity * i.unit_price - (i.discount or 0)
        share = left if k == len(elig) - 1 else amount * line_base // base
        i.discount = (i.discount or 0) + share
        left -= share
    for i in items:
        i.line_total = i.quantity * i.unit_price - (i.discount or 0)
    return amount


def recalc_order(order: Order) -> None:
    """UC30: tính `subtotal`, `discount`, `shipping_fee`, `grand_total` từ `order.items`."""
    items = getattr(order, "items", [])
    for i in items:
        i.discount = i.discount or 0
        i.line_total = i.quantity * i.unit_price - i.discount
    order.subtotal = sum(i.quantity * i.unit_price for i in items)
    order.discount = sum(i.discount for i in items)
    order.shipping_fee = shipping_fee(order.delivery_service, order.subtotal - order.discount)
    order.grand_total = order.subtotal - order.discount + order.shipping_fee


def voucher_error(voucher: Voucher | None, promotion: Promotion | None, subtotal: int,
                  cart_style_ids: set[int], promotion_style_ids: set[int],
                  applied_codes: set[str], now: datetime) -> str | None:
    """UC26: lý do voucher không dùng được (theo thứ tự kiểm tra), `None` nếu hợp lệ."""
    if voucher is None or promotion is None:
        return "Mã giảm giá không tồn tại"
    if promotion.status != PromotionStatus.ACTIVE:
        return "Chương trình khuyến mãi không còn hoạt động"
    if not (promotion.starts_at <= now < promotion.ends_at):
        return "Mã chưa đến hoặc đã hết thời gian áp dụng"
    if voucher.used_count >= voucher.usage_limit:
        return "Mã đã hết lượt sử dụng"
    if subtotal < (promotion.min_order_value or 0):
        return f"Đơn tối thiểu {promotion.min_order_value:,} đ để dùng mã này".replace(",", ".")
    if not (cart_style_ids & promotion_style_ids):
        return "Giỏ hàng không có sản phẩm thuộc chương trình"
    if voucher.code.upper() in {c.upper() for c in applied_codes}:
        return "Mã này đã được áp dụng"
    return None


def net_paid(payments: list[Payment]) -> int:
    """Số tiền đã thu ròng = Σ charge succeeded − Σ refund succeeded."""
    total = 0
    for p in payments:
        if p.status != PaymentStatus.SUCCEEDED:
            continue
        total += p.amount if p.kind == PaymentKind.CHARGE else -p.amount
    return total
