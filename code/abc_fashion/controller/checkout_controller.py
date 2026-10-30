"""CheckoutController — thanh toán (UC08 + UC26, UC28–UC31) và thanh toán lại đơn chờ thanh toán."""
from __future__ import annotations

from datetime import datetime

from abc_fashion.control.dao.address_dao import AddressDAO
from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.payment_method_dao import PaymentMethodDAO
from abc_fashion.control.dao.promotion_dao import PromotionDAO
from abc_fashion.control.dao.voucher_dao import VoucherDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.controller import _flows
from abc_fashion.controller._errors import AccessDenied, BusinessError
from abc_fashion.model.catalogue import Style
from abc_fashion.model.customer_data import LinkedMethodType, Address, PaymentMethod
from abc_fashion.model.sales import (DeliveryService, OrderStatus, PaymentMethodType, apply_discount, promo_price,
                                     promotion_amount, recalc_order, voucher_error, Cart, Order, OrderItem, Voucher)
from abc_fashion.model.user import Customer

LINKED_FOR = {PaymentMethodType.CARD: LinkedMethodType.CARD, PaymentMethodType.E_WALLET: LinkedMethodType.E_WALLET}


class CheckoutController:
    def __init__(self):
        self.address_dao = AddressDAO()
        self.payment_method_dao = PaymentMethodDAO()
        self.voucher_dao = VoucherDAO()
        self.order_dao = OrderDAO()
        self.payment_dao = PaymentDAO()
        self.notification_dao = NotificationDAO()
        self.promotion_dao = PromotionDAO()
        self.payment_gateway = PaymentGateway()
        self.notification_gateway = NotificationGateway()

    # ---------- chuẩn bị đơn ----------
    def start_checkout(self, customer: Customer, cart: Cart) -> Order:
        """Đơn nháp từ giỏ: giá đã trừ khuyến mãi tự động (UC31), `order.vouchers` rỗng, tổng đã tính."""
        order = Order(delivery_service=DeliveryService.STANDARD, customerId=customer.id)
        promos: dict[int, object] = {}
        order.items = []
        for c in cart.items:
            if c.styleId not in promos:
                p = self.promotion_dao.get_active_promotion_by_style(Style(id=c.styleId))
                promos[c.styleId] = p if p is not None and not getattr(p, "voucher_count", 0) else None
            it = OrderItem(productVariantId=c.productVariantId, quantity=c.quantity,
                           unit_price=promo_price(c.price, promos[c.styleId]), discount=0, sku=c.sku,
                           size_label=c.size_label, colour=c.colour, price=c.price, styleId=c.styleId)
            it.style_name = c.style_name
            order.items.append(it)
        order.vouchers = []
        return self.recalc(order)

    def recalc(self, order: Order) -> Order:
        """UC26 + UC30: phân bổ lại giảm giá của mọi voucher đã áp, rồi tính phí ship và tổng."""
        items = order.items
        for i in items:
            i.discount = 0
        for v in getattr(order, "vouchers", []):
            p = v.promotion
            elig = [i for i in items if i.styleId in p.style_ids]
            base = sum(i.quantity * i.unit_price - i.discount for i in elig)
            apply_discount(items, p.style_ids, promotion_amount(p, base))
        recalc_order(order)
        return order

    def get_addresses(self, customer: Customer) -> list[Address]:
        return self.address_dao.get_address_by_customer(customer)

    def get_payment_options(self, customer: Customer, method_type: PaymentMethodType) -> list[PaymentMethod | None]:
        """Phương thức đã liên kết dùng được cho `method_type`; ví điện tử còn có lựa chọn None (trả trên ví)."""
        linked = LINKED_FOR.get(method_type)
        if linked is None:
            return []
        options: list[PaymentMethod | None] = [m for m in self.payment_method_dao.get_payment_method_by_customer(customer)
                                               if m.method_type == linked]
        if method_type == PaymentMethodType.E_WALLET:
            options.append(None)
        return options

    def apply_voucher(self, order: Order, code: str) -> Voucher:
        code = (code or "").strip()
        if not code:
            raise BusinessError("Nhập mã giảm giá")
        voucher = self.voucher_dao.get_voucher_by_code(code)
        promotion = voucher.promotion if voucher else None
        error = voucher_error(voucher, promotion, order.subtotal, {i.styleId for i in order.items},
                              promotion.style_ids if promotion else set(), {v.code for v in order.vouchers},
                              datetime.now())
        if error:
            raise BusinessError(error)
        order.vouchers.append(voucher)
        self.recalc(order)
        return voucher

    # ---------- đặt hàng ----------
    def place_order(self, customer: Customer, order: Order, address: Address | None, method_type: PaymentMethodType,
                    method: PaymentMethod | None, note: str) -> bool:
        """UC08: (1) giữ hàng + ghi đơn, (2) thu tiền, (3) xác nhận + thông báo. Trả True nếu đơn đã xác nhận,
        False nếu thanh toán bị từ chối (đơn vẫn giữ hàng, chờ thanh toán lại).

        Sau bước (1) `order.id` có giá trị. Ngân hàng không phản hồi ở bước (2) → ServiceUnavailable: đơn đã giữ,
        view chuyển sang màn hình kết quả để thanh toán lại thay vì đặt đơn lần hai.
        """
        if address is None:
            raise BusinessError("Chọn hoặc thêm địa chỉ giao hàng")
        if method_type == PaymentMethodType.CARD and method is None:
            raise BusinessError("Chọn thẻ đã liên kết (liên kết thẻ trong Hồ sơ)")
        if method_type not in LINKED_FOR:
            method = None
        order.note = (note or "").strip() or None
        order.ship_recipient, order.ship_phone, order.ship_address = address.recipient_name, address.phone, \
            address.one_line()
        self.recalc(order)
        if not self.order_dao.add_order(order, customer):                                    # (1)
            raise BusinessError("Sản phẩm vừa hết hàng hoặc mã giảm giá vừa hết lượt. Vui lòng quay lại giỏ.")
        return _flows.pay_order(self, order, customer, method_type, method)                 # (2) + (3)

    # ---------- kết quả / thanh toán lại ----------
    def get_order(self, customer: Customer, order: Order) -> Order:
        o = self.order_dao.get_order_detail(order)
        if o is None or o.customerId != customer.id:
            raise AccessDenied("Bạn không xem được đơn hàng này")
        return o

    def get_retry_options(self, customer: Customer) -> list[tuple[PaymentMethodType, PaymentMethod | None]]:
        """Các cách thanh toán lại: thẻ / ví đã liên kết, chuyển khoản, COD."""
        out = []
        for m in self.payment_method_dao.get_payment_method_by_customer(customer):
            if m.method_type == LinkedMethodType.CARD:
                out.append((PaymentMethodType.CARD, m))
            elif m.method_type == LinkedMethodType.E_WALLET:
                out.append((PaymentMethodType.E_WALLET, m))
        return out + [(PaymentMethodType.BANK_TRANSFER, None), (PaymentMethodType.COD, None)]

    def retry_payment(self, customer: Customer, order: Order, method_type: PaymentMethodType,
                      method: PaymentMethod | None) -> bool:
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise BusinessError("Đơn không còn chờ thanh toán")
        return _flows.pay_order(self, order, customer, method_type, method)
