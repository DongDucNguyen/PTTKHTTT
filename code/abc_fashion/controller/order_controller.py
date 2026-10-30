"""OrderController — đơn hàng của khách: danh sách, chi tiết, huỷ / yêu cầu huỷ, nhận hàng, theo dõi kiện (UC09–UC12)."""
from __future__ import annotations

from datetime import datetime

from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.control.dao.review_dao import ReviewDAO
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.controller import _flows
from abc_fashion.controller._errors import AccessDenied, BusinessError
from abc_fashion.model.fulfilment import ShipmentDirection, Shipment, ShipmentEvent
from abc_fashion.model.returns import within_return_window
from abc_fashion.model.sales import ORDER_CANCELLABLE, OrderStatus, Order
from abc_fashion.model.user import Customer


class OrderController:
    def __init__(self):
        self.order_dao = OrderDAO()
        self.payment_dao = PaymentDAO()
        self.shipment_dao = ShipmentDAO()
        self.return_request_dao = ReturnRequestDAO()
        self.review_dao = ReviewDAO()
        self.notification_dao = NotificationDAO()
        self.payment_gateway = PaymentGateway()
        self.shipping_gateway = ShippingGateway()
        self.notification_gateway = NotificationGateway()

    def get_orders(self, customer: Customer, status: OrderStatus | None) -> list[Order]:
        return self.order_dao.get_order_by_customer(customer, status)

    def get_order_detail(self, customer: Customer, order: Order) -> Order:
        """Đơn đầy đủ của chính khách (NFR03, khác → AccessDenied), gắn động: `return_request`, `delivered_at`,
        mỗi dòng `reviewed` / `can_review`, và quyền thao tác `can_track`, `can_cancel`, `can_confirm_received`,
        `can_return`."""
        o = self.order_dao.get_order_detail(order)
        if o.customerId != customer.id:
            raise AccessDenied("Bạn không xem được đơn hàng này")
        o.return_request = self.return_request_dao.get_return_request_by_order(o)
        done = o.status in (OrderStatus.DELIVERED, OrderStatus.COMPLETED)
        for i in o.items:
            i.reviewed = self.review_dao.is_reviewed(i)
            i.can_review = done and not i.reviewed
        times = [s.delivered_at for s in o.shipments
                 if s.direction == ShipmentDirection.OUTBOUND and s.returnRequestId is None and s.delivered_at]
        o.delivered_at = max(times) if times else None
        o.can_track = bool(o.shipments)
        o.can_cancel = o.status in ORDER_CANCELLABLE and not (o.status == OrderStatus.PROCESSING and o.cancel_reason)
        o.can_confirm_received = o.status == OrderStatus.DELIVERED
        o.can_return = done and o.return_request is None and within_return_window(o.delivered_at, datetime.now())
        return o

    def get_order_signature(self, order: Order) -> tuple:
        """Dấu hiệu thay đổi (trạng thái đơn và các kiện) để màn hình tự nạp lại khi vận chuyển tiến triển."""
        return self.order_dao._status_signature(order.id)

    def cancel_order(self, order: Order, reason: str) -> tuple[str, str | None]:
        """UC10: đơn chưa đóng gói → huỷ ngay và hoàn tiền; đơn đang đóng gói → gửi yêu cầu huỷ cho quản lý.

        Trả `(thông_báo, cảnh_báo)`; cảnh báo khác None khi đã huỷ nhưng ngân hàng chưa hoàn được tiền.
        """
        reason = (reason or "").strip()
        if not reason:
            raise BusinessError("Chọn hoặc nhập lý do huỷ")
        if order.status in (OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED):
            ok, warning = _flows.cancel_with_refund(self, order, reason)
            if not ok:
                raise BusinessError("Đơn vừa thay đổi trạng thái, không huỷ được nữa")
            return "Đơn đã được huỷ", warning
        if order.status == OrderStatus.PROCESSING:
            # thiết kế chưa có trạng thái "yêu cầu huỷ": lưu cancel_reason, trạng thái giữ nguyên (mục 13 #12)
            order.cancel_reason = reason
            if not self.order_dao._request_cancel(order):
                raise BusinessError("Đơn vừa thay đổi trạng thái, không gửi được yêu cầu huỷ")
            return "Đã gửi yêu cầu huỷ, quản lý sẽ xem xét", None
        raise BusinessError("Đơn đã giao cho hãng vận chuyển nên không huỷ được. Bạn có thể yêu cầu trả hàng.")

    def confirm_received(self, order: Order) -> bool:
        """UC12: khách xác nhận đã nhận đủ hàng → hoàn tất."""
        order.status = OrderStatus.COMPLETED
        if not self.order_dao.update_order_status(order):
            raise BusinessError("Trạng thái đơn vừa thay đổi, vui lòng xem lại")
        return True

    # ---------- theo dõi kiện (UC11) ----------
    def get_shipment(self, shipment: Shipment) -> Shipment:
        """Kiện mới nhất trong CSDL (kèm `records`)."""
        return next((s for s in self.shipment_dao.get_shipment_by_order(Order(id=shipment.orderId))
                     if s.id == shipment.id), shipment)

    def get_shipment_events(self, shipment: Shipment) -> list[ShipmentEvent]:
        return self.shipment_dao.get_shipment_event(shipment)

    def get_shipment_signature(self, shipment: Shipment) -> tuple:
        return (self.get_shipment(shipment).status, len(self.get_shipment_events(shipment)))

    def refresh_tracking(self, shipment: Shipment) -> int:
        """Hỏi hãng vận chuyển, ghi sự kiện mới; trả số sự kiện mới."""
        if not shipment.tracking_no:
            return 0
        return sum(self.shipment_dao.add_shipment_event(e, shipment)
                   for e in self.shipping_gateway.get_tracking(shipment))
