"""Luồng nghiệp vụ dùng chung giữa nhiều controller (module riêng tư của controller layer).

Các hàm nhận `ctrl` là controller có sẵn các DAO / gateway cần dùng (ghi trong docstring từng hàm).
Quy tắc mục 11: không gọi gateway trong transaction — ghi CSDL, commit, gọi gateway, rồi ghi kết quả.
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime

from abc_fashion.control.gateway import _http
from abc_fashion.control.gateway._http import GatewayUnavailable
from abc_fashion.controller._media import media_path
from abc_fashion.model.customer_data import Channel, NotificationEvent, NotificationStatus, Notification
from abc_fashion.model.sales import (OrderStatus, PaymentKind, PaymentMethodType, PaymentStatus, net_paid, Order,
                                     Payment)
from abc_fashion.model.user import Customer

log = logging.getLogger("abc_fashion")


def money(x: int | None) -> str:
    return f"{x or 0:,}".replace(",", ".") + " đ"


def notify(gateway, dao, customer_id: int, event: NotificationEvent, message: str) -> bool:
    """Gửi thông báo qua NotificationGateway rồi ghi Notification (sent / failed). Lỗi gửi không chặn nghiệp vụ."""
    n = Notification(channel=Channel.EMAIL, event_type=event, message=message, customerId=customer_id)
    try:
        n.recipient = dao._get_recipient(customer_id)[0]          # dịch vụ e-mail cần địa chỉ nhận
    except Exception:                               # noqa: BLE001 - thiếu địa chỉ không chặn nghiệp vụ
        log.exception("recipient")
    try:
        ok = gateway.send(n)
    except Exception:                               # noqa: BLE001 - lỗi gửi không chặn nghiệp vụ
        log.exception("NotificationGateway.send")
        ok = False
    n.status = NotificationStatus.SENT if ok else NotificationStatus.FAILED
    n.sent_at = datetime.now() if ok else None
    dao.add_notification(n, Customer(id=customer_id))
    return ok


def notify_customer(ctrl, customer_id: int, event: NotificationEvent, message: str) -> bool:
    """`ctrl` phải có notification_gateway, notification_dao."""
    return notify(ctrl.notification_gateway, ctrl.notification_dao, customer_id, event, message)


def pay_order(ctrl, order: Order, customer: Customer, mtype: PaymentMethodType, method) -> bool:
    """Bước (2)–(3) của UC08: thu tiền (hoặc COD), xác nhận đơn, gửi thông báo.

    `ctrl` phải có order_dao, payment_dao, payment_gateway, notification_dao, notification_gateway.
    Ngân hàng không phản hồi → GatewayUnavailable (đơn vẫn giữ hàng ở trạng thái chờ thanh toán).
    """
    if mtype == PaymentMethodType.COD:
        ctrl.payment_dao.add_payment(Payment(kind=PaymentKind.CHARGE, method=mtype, amount=order.grand_total,
                                             status=PaymentStatus.PENDING), order)
        ok = True
    else:
        ok, ref = ctrl.payment_gateway.charge(order, method)
        ctrl.payment_dao.add_payment(Payment(kind=PaymentKind.CHARGE, method=mtype, amount=order.grand_total,
                                             status=PaymentStatus.SUCCEEDED if ok else PaymentStatus.FAILED,
                                             transaction_ref=ref, paymentMethodId=method.id if method else None),
                                     order)
    if not ok:
        return False
    order.status = OrderStatus.CONFIRMED
    if not ctrl.order_dao.update_order_status(order):
        return False
    notify_customer(ctrl, customer.id, NotificationEvent.ORDER_CONFIRMED,
                    f"Đơn {order.order_no} ({money(order.grand_total)}) đã được xác nhận.")
    return True


def refund_order(ctrl, order: Order, amount: int) -> tuple[bool, int]:
    """Hoàn `amount` (không vượt số đã thu ròng) cho lần thu thành công gần nhất của đơn.

    `ctrl` phải có payment_dao, payment_gateway. Trả `(thành_công, số_tiền_hoàn)`. Ngân hàng không phản hồi →
    ghi lần hoàn thất bại để đối soát rồi ném GatewayUnavailable.
    """
    payments = ctrl.payment_dao.get_payment_by_order(order)
    amount = min(amount, net_paid(payments))
    charges = [p for p in payments if p.kind == PaymentKind.CHARGE and p.status == PaymentStatus.SUCCEEDED]
    if amount <= 0 or not charges:
        return False, 0
    charge = charges[-1]
    refund = Payment(kind=PaymentKind.REFUND, method=charge.method, amount=amount,
                     transaction_ref=charge.transaction_ref, paymentMethodId=charge.paymentMethodId)
    try:
        ok, ref = ctrl.payment_gateway.refund(refund)
    except GatewayUnavailable:
        refund.status, refund.transaction_ref = PaymentStatus.FAILED, None
        ctrl.payment_dao.add_payment(refund, order)
        raise
    refund.status, refund.transaction_ref = (PaymentStatus.SUCCEEDED if ok else PaymentStatus.FAILED), ref
    ctrl.payment_dao.add_payment(refund, order)
    return ok, amount if ok else 0


def cancel_with_refund(ctrl, order: Order, reason: str) -> tuple[bool, str | None]:
    """UC10 / UC23: huỷ đơn (tồn kho, voucher trong DAO), huỷ COD chưa thu, hoàn tiền đã thu, thông báo.

    `ctrl` phải có order_dao, payment_dao, payment_gateway, notification_dao, notification_gateway.
    Trả `(đã_huỷ, cảnh_báo)`; cảnh báo khác None khi đơn đã huỷ nhưng ngân hàng không phản hồi để hoàn tiền.
    """
    order.cancel_reason = reason
    if not ctrl.order_dao.cancel_order(order):
        return False, None
    for p in ctrl.payment_dao.get_payment_by_order(order):
        if p.status == PaymentStatus.PENDING and p.method == PaymentMethodType.COD:
            p.status = PaymentStatus.FAILED
            ctrl.payment_dao.update_payment(p)
    warning = None
    try:
        _, refunded = refund_order(ctrl, order, order.grand_total)
    except GatewayUnavailable:                      # đơn đã huỷ; tiền hoàn lại sau ở ManageOrderFrm ("Hoàn tiền…")
        refunded = 0
        warning = (f"Đơn {order.order_no} đã huỷ nhưng cổng thanh toán không phản hồi nên chưa hoàn được tiền. "
                   "Nhân viên sẽ hoàn lại sau.")
    notify_customer(ctrl, order.customerId, NotificationEvent.ORDER_CANCELLED,
                    f"Đơn {order.order_no} đã được huỷ. Lý do: {reason}")
    if refunded:
        notify_customer(ctrl, order.customerId, NotificationEvent.REFUND_COMPLETED,
                        f"Đã hoàn {money(refunded)} cho đơn {order.order_no}.")
    return True, warning


def push_search_index(style_dao, search_engine) -> None:
    """Đẩy danh mục sản phẩm lên dịch vụ AI (chỉ ở chế độ http): đọc CSDL ở luồng gọi, gửi ở luồng phụ.

    Dịch vụ AI chưa chạy thì chỉ ghi log: tìm bằng ảnh / giọng nói sẽ báo lỗi, phần còn lại vẫn dùng được.
    """
    if not _http.use_http():
        return
    try:
        styles = style_dao._get_catalogue_for_index()
    except Exception:                                       # noqa: BLE001
        log.exception("push_search_index: đọc danh mục")
        return
    entries = [{"id": s.id, "code": s.code, "name": s.name, "brand": s.brand or "", "description": s.description or "",
                "category": getattr(s, "category_name", ""), "colours": list(getattr(s, "colours", []) or []),
                "image_path": media_path(getattr(s, "image_url", None))} for s in styles]

    def work():
        try:
            info = search_engine._push_index(entries)
            log.info("Đã đẩy chỉ mục tìm kiếm lên dịch vụ AI: %s", info)
        except Exception as e:                              # noqa: BLE001
            log.warning("Không đẩy được chỉ mục lên dịch vụ AI: %s", e)

    threading.Thread(target=work, daemon=True).start()
