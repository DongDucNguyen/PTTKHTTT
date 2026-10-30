"""Quy tắc thuần của model: tiền, giảm giá, voucher, máy trạng thái, hoàn tiền (không cần CSDL)."""
from datetime import datetime, timedelta

import pytest

from abc_fashion.control.dao.dao import _check_password, _hash_password, _to_entity
from abc_fashion.model.catalogue import Category
from abc_fashion.model.catalogue import category_descendants
from abc_fashion.model.fulfilment import ShipmentDirection, ShipmentStatus, order_status_from_shipments, Shipment
from abc_fashion.model.inventory import availability_text, StockLevel
from abc_fashion.model.returns import InspectionResult, refund_amount, refund_line, ReturnItem, within_return_window
from abc_fashion.model.sales import (ORDER_NEXT, DeliveryService, DiscountType, OrderStatus, PaymentKind, PaymentStatus,
                                     PromotionStatus, apply_discount, can_transition, net_paid, promo_price,
                                     promotion_amount, recalc_order, shipping_fee, Order, OrderItem, Payment,
                                     Promotion, Voucher, voucher_error)
from abc_fashion.model.user import AccountStatus, Customer

NOW = datetime(2026, 10, 29, 12, 0)


def _items():
    return [OrderItem(productVariantId=1, styleId=1, quantity=1, unit_price=450_000, discount=0),
            OrderItem(productVariantId=5, styleId=3, quantity=3, unit_price=250_000, discount=0),
            OrderItem(productVariantId=3, styleId=2, quantity=1, unit_price=333_333, discount=0)]


def _promo(**kw):
    base = dict(id=1, name="P", discount_type=DiscountType.PERCENT, discount_value=10, min_order_value=300_000,
                starts_at=NOW - timedelta(days=1), ends_at=NOW + timedelta(days=1), status=PromotionStatus.ACTIVE)
    return Promotion(**{**base, **kw})


def test_discount_allocation_sums_exactly():
    items = _items()
    got = apply_discount(items, {1, 2}, 77_777)
    assert got == 77_777
    assert sum(i.discount for i in items) == 77_777
    assert items[1].discount == 0                                  # style 3 không đủ điều kiện
    for i in items:
        assert i.line_total == i.quantity * i.unit_price - i.discount


def test_discount_capped_at_eligible_base():
    items = _items()
    assert apply_discount(items, {1}, 10_000_000) == 450_000
    assert items[0].line_total == 0


def test_recalc_order_satisfies_check_constraints():
    o = Order(delivery_service=DeliveryService.EXPRESS)
    o.items = _items()
    apply_discount(o.items, {2}, 50_000)
    recalc_order(o)
    assert o.subtotal == 450_000 + 750_000 + 333_333
    assert o.discount == 50_000
    assert o.shipping_fee == 0                                     # ≥ 500.000 đ sau giảm → miễn phí
    assert o.grand_total == o.subtotal - o.discount + o.shipping_fee


def test_shipping_fee_table():
    assert shipping_fee(DeliveryService.STANDARD, 499_999) == 30_000
    assert shipping_fee(DeliveryService.EXPRESS, 100_000) == 50_000
    assert shipping_fee(DeliveryService.STANDARD, 500_000) == 0


def test_promotion_amount_and_price():
    assert promotion_amount(_promo(), 450_000) == 45_000
    assert promotion_amount(_promo(discount_type=DiscountType.FIXED_AMOUNT, discount_value=50_000), 30_000) == 30_000
    assert promo_price(250_000, _promo(discount_type=DiscountType.FIXED_AMOUNT, discount_value=50_000)) == 200_000
    assert promo_price(250_000, None) == 250_000


@pytest.mark.parametrize("kw, subtotal, styles, applied, expect", [
    ({}, 500_000, {1}, set(), None),
    ({"status": PromotionStatus.ENDED}, 500_000, {1}, set(), "không còn hoạt động"),
    ({"ends_at": NOW - timedelta(hours=1)}, 500_000, {1}, set(), "thời gian"),
    ({}, 100_000, {1}, set(), "tối thiểu"),
    ({}, 500_000, {9}, set(), "không có sản phẩm"),
    ({}, 500_000, {1}, {"xuanhe10"}, "đã được áp dụng"),
])
def test_voucher_error_order(kw, subtotal, styles, applied, expect):
    v = Voucher(code="XUANHE10", usage_limit=10, used_count=0)
    err = voucher_error(v, _promo(**kw), subtotal, styles, {1, 2}, applied, NOW)
    assert (err is None) if expect is None else (expect in err)


def test_voucher_used_up_and_missing():
    used = Voucher(code="HETLUOT", usage_limit=1, used_count=1)
    assert "hết lượt" in voucher_error(used, _promo(), 500_000, {1}, {1}, set(), NOW)
    assert "không tồn tại" in voucher_error(None, None, 0, set(), set(), set(), NOW)


def test_order_state_machine():
    assert can_transition(OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED)
    assert not can_transition(OrderStatus.PENDING_PAYMENT, OrderStatus.SHIPPED)
    assert not can_transition(OrderStatus.SHIPPED, OrderStatus.CANCELLED)          # huỷ sau khi giao bị từ chối
    assert not can_transition(OrderStatus.COMPLETED, OrderStatus.DELIVERED)
    assert all(not ORDER_NEXT[s] for s in (OrderStatus.COMPLETED, OrderStatus.CANCELLED))


def test_order_status_from_shipments():
    def s(st, d=ShipmentDirection.OUTBOUND, rr=None):
        return Shipment(direction=d, status=st, returnRequestId=rr)
    assert order_status_from_shipments([s(ShipmentStatus.REQUESTED)] * 2) is None
    assert order_status_from_shipments([s(ShipmentStatus.PICKED_UP), s(ShipmentStatus.REQUESTED)]) == OrderStatus.PARTIALLY_SHIPPED
    assert order_status_from_shipments([s(ShipmentStatus.PICKED_UP), s(ShipmentStatus.IN_TRANSIT)]) == OrderStatus.SHIPPED
    assert order_status_from_shipments([s(ShipmentStatus.DELIVERED), s(ShipmentStatus.DELIVERED),
                                        s(ShipmentStatus.REQUESTED, ShipmentDirection.RETURN, 1)]) == OrderStatus.DELIVERED


def test_net_paid():
    pays = [Payment(kind=PaymentKind.CHARGE, amount=950_000, status=PaymentStatus.FAILED),
            Payment(kind=PaymentKind.CHARGE, amount=950_000, status=PaymentStatus.SUCCEEDED),
            Payment(kind=PaymentKind.REFUND, amount=250_000, status=PaymentStatus.SUCCEEDED)]
    assert net_paid(pays) == 700_000


def test_refund_with_line_discount():
    # mua 3 × 250.000, giảm dòng 30.000 → trả 2: 500.000 − 30.000×2/3 = 480.000
    assert refund_line(2, 250_000, 30_000, 3) == 480_000
    items = [ReturnItem(quantity=2, unit_price=250_000, discount=30_000, inspection_result=InspectionResult.PASSED),
             ReturnItem(quantity=1, unit_price=450_000, discount=0, inspection_result=InspectionResult.FAILED)]
    items[0].ordered_quantity, items[1].ordered_quantity = 3, 1
    assert refund_amount(items) == 480_000                          # hàng FAILED không hoàn


def test_return_window():
    assert within_return_window(NOW - timedelta(days=29), NOW)
    assert not within_return_window(NOW - timedelta(days=31), NOW)
    assert not within_return_window(None, NOW)


def test_availability_text():
    assert availability_text(None) == "Hết hàng"
    assert availability_text(StockLevel(available=0, reorder_point=3)) == "Hết hàng"
    assert availability_text(StockLevel(available=2, reorder_point=3)) == "Chỉ còn 2"
    assert availability_text(StockLevel(available=20, reorder_point=3)) == "Còn hàng"


def test_category_descendants_blocks_cycles():
    cats = [Category(id=1, parentId=None), Category(id=3, parentId=1), Category(id=7, parentId=3)]
    assert category_descendants(cats, 1) == {1, 3, 7}


def test_password_hash_roundtrip():
    h = _hash_password("abc12345")
    assert h.startswith("pbkdf2$") and "abc12345" not in h
    assert _check_password("abc12345", h) and not _check_password("wrong", h)
    assert _check_password("abc12345", "abc12345")                 # dữ liệu mẫu bản rõ (mục 13 #15)


def test_to_entity_enum_and_extras():
    c = _to_entity(Customer, {"id": 3, "status": "active", "full_name": "A", "userId": 9, "style_name": "x"})
    assert c.status == AccountStatus.ACTIVE and c.id == 3 and c.userId == 9 and c.style_name == "x"


def test_bcrypt_passwords_from_report_db():
    import bcrypt
    stored = bcrypt.hashpw(b"abc12345", bcrypt.gensalt(4)).decode()
    assert _check_password("abc12345", stored) and not _check_password("x", stored)
    assert not _check_password("abc12345", "$2b$12$" + "A" * 54)          # hash hỏng → False, không lỗi


def test_view_helpers_without_display():
    from abc_fashion.model.catalogue import FitType
    from abc_fashion.model.sales import PromoType
    from abc_fashion.view._util import label, ship_text
    assert ship_text(Order(ship_recipient="An", ship_phone="0900", ship_address="1 Lê Lợi")) == "An – 0900 – 1 Lê Lợi"
    assert "đơn cũ" in ship_text(Order())                      # đơn chưa có địa chỉ chụp (dữ liệu báo cáo)
    assert label(PromoType.FLASH_SALE) == "Flash sale" and label(FitType.SLIM).startswith("Ôm")
    assert label(None) == ""
