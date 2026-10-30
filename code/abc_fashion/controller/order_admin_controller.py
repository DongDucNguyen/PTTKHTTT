"""OrderAdminController — quản lý đơn: tìm, chuyển trạng thái + bàn giao kiện, huỷ, duyệt yêu cầu huỷ, hoàn tiền
(UC22, UC23, UC10)."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.audit_log_entry_dao import AuditLogEntryDAO
from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.controller import _flows
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.audit import AuditAction, AuditLogEntry
from abc_fashion.model.customer_data import NotificationEvent
from abc_fashion.model.fulfilment import (ShipmentDirection, ShipmentStatus, order_status_from_shipments, Shipment,
                                          ShipmentEvent)
from abc_fashion.model.sales import (ORDER_CANCELLABLE, ORDER_NEXT, OrderStatus, PaymentMethodType, PaymentStatus,
                                     net_paid, Order)
from abc_fashion.model.user import StaffMember


def _ship_text(order: Order) -> str:
    parts = [p for p in (order.ship_recipient, order.ship_phone, order.ship_address) if p]
    return " – ".join(parts) if parts else "(đơn cũ — chưa lưu địa chỉ giao hàng)"


class OrderAdminController:
    def __init__(self):
        self.order_dao = OrderDAO()
        self.shipment_dao = ShipmentDAO()
        self.payment_dao = PaymentDAO()
        self.notification_dao = NotificationDAO()
        self.audit_log_entry_dao = AuditLogEntryDAO()
        self.payment_gateway = PaymentGateway()
        self.shipping_gateway = ShippingGateway()
        self.notification_gateway = NotificationGateway()

    def search_order(self, key: str, status: OrderStatus | None, start: date, end: date) -> list[Order]:
        if start > end:
            raise BusinessError("Ngày bắt đầu phải trước ngày kết thúc")
        return self.order_dao.search_order(key or "", status, start, end)

    def get_order_detail(self, order: Order) -> Order:
        """Đơn đầy đủ, gắn động: `next_statuses` (theo ORDER_NEXT, trừ huỷ), `can_cancel`, `cancel_requested`,
        `paid` (đã thu ròng), `can_refund`."""
        o = self.order_dao.get_order_detail(order)
        o.next_statuses = sorted(ORDER_NEXT[o.status] - {OrderStatus.CANCELLED}, key=lambda s: list(OrderStatus).index(s))
        o.can_cancel = o.status in ORDER_CANCELLABLE
        o.cancel_requested = bool(o.cancel_reason) and o.can_cancel
        o.paid = net_paid(o.payments)
        o.can_refund = o.paid > 0
        return o

    def get_order_signature(self, order: Order) -> tuple:
        return self.order_dao._status_signature(order.id)

    @staticmethod
    def _outbound(order: Order) -> list[Shipment]:
        return [s for s in order.shipments if s.direction == ShipmentDirection.OUTBOUND and s.returnRequestId is None]

    def _dispatch(self, order: Order, shipments: list[Shipment]) -> None:
        """Bàn giao kiện cho hãng: ShippingGateway.create_shipment → carrier, tracking_no; kiện → picked_up."""
        for s in shipments:
            s.from_location = getattr(s, "location_name", "")
            s.to_address = _ship_text(order)
            s.carrier, s.tracking_no = self.shipping_gateway.create_shipment(s)
            s.status = ShipmentStatus.PICKED_UP
            self.shipment_dao.update_shipment(s)
            self.shipment_dao.add_shipment_event(
                ShipmentEvent(status=ShipmentStatus.PICKED_UP, occurred_at=None, note="Bàn giao cho hãng vận chuyển"), s)

    def update_status(self, staff: StaffMember, order: Order, new_status: OrderStatus,
                      shipments: list[Shipment]) -> OrderStatus:
        """Chuyển đơn sang `new_status`. Giao (một phần) thì bàn giao các kiện chờ lấy hàng — `shipments` là kiện được
        chọn khi giao một phần. Trả trạng thái mới (suy từ các kiện khi giao)."""
        o, new = order, new_status
        if new in (OrderStatus.PARTIALLY_SHIPPED, OrderStatus.SHIPPED):
            waiting = [s for s in self._outbound(o) if s.status == ShipmentStatus.REQUESTED]
            chosen = ([s for s in waiting if s.id in {x.id for x in shipments}]
                      if new == OrderStatus.PARTIALLY_SHIPPED else waiting)
            if not chosen:
                raise BusinessError("Chọn kiện (đang chờ lấy hàng) muốn giao")
            self._dispatch(o, chosen)
            new = order_status_from_shipments(self._outbound(o)) or new
            if new == OrderStatus.PARTIALLY_SHIPPED and o.status == OrderStatus.PARTIALLY_SHIPPED:
                return o.status                                  # giao thêm kiện, đơn vẫn giao một phần
        o.status = new
        if not self.order_dao.update_order_status(o):
            raise BusinessError("Không chuyển được trạng thái (đơn vừa được người khác cập nhật?)")
        if new in (OrderStatus.PARTIALLY_SHIPPED, OrderStatus.SHIPPED):
            _flows.notify_customer(self, o.customerId, NotificationEvent.ORDER_SHIPPED,
                                   f"Đơn {o.order_no} đã được giao cho hãng vận chuyển.")
        elif new == OrderStatus.DELIVERED:
            for p in o.payments:                       # COD: thu tiền khi giao
                if p.method == PaymentMethodType.COD and p.status == PaymentStatus.PENDING:
                    p.status, p.transaction_ref = PaymentStatus.SUCCEEDED, f"COD-{o.order_no}"
                    self.payment_dao.update_payment(p)
            _flows.notify_customer(self, o.customerId, NotificationEvent.ORDER_DELIVERED,
                                   f"Đơn {o.order_no} đã giao thành công.")
        return o.status

    def cancel_order(self, staff: StaffMember, order: Order, reason: str) -> str | None:
        """UC23 / duyệt yêu cầu huỷ của khách: huỷ, trả hàng về kho, hoàn tiền, ghi nhật ký.
        Trả cảnh báo nếu ngân hàng chưa hoàn được tiền (đơn vẫn đã huỷ)."""
        reason = (reason or "").strip()
        if not reason:
            raise BusinessError("Nhập lý do huỷ")
        ok, warning = _flows.cancel_with_refund(self, order, reason)
        if not ok:
            raise BusinessError("Không huỷ được: đơn đã bàn giao vận chuyển hoặc vừa thay đổi")
        self.audit_log_entry_dao.add_audit_log_entry(
            AuditLogEntry(entity=f"tblOrder#{order.id}", action=AuditAction.UPDATE,
                          changes=f"status -> cancelled; lý do: {reason}"), staff)
        return warning

    def refund(self, staff: StaffMember, order: Order, amount: int) -> int:
        """Hoàn tiền thủ công (vd. lần hoàn khi huỷ bị lỗi ngân hàng); trả số đã hoàn."""
        if not amount or amount <= 0:
            raise BusinessError("Số tiền hoàn phải lớn hơn 0")
        ok, refunded = _flows.refund_order(self, order, amount)
        if not ok:
            raise BusinessError("Cổng thanh toán từ chối hoàn tiền")
        _flows.notify_customer(self, order.customerId, NotificationEvent.REFUND_COMPLETED,
                               f"Đã hoàn {_flows.money(refunded)} cho đơn {order.order_no}.")
        self.audit_log_entry_dao.add_audit_log_entry(
            AuditLogEntry(entity=f"tblOrder#{order.id}", action=AuditAction.UPDATE, changes=f"refund {refunded}"), staff)
        return refunded
