"""SyncController — tác vụ nền khi nối dịch vụ ngoài: đồng bộ vận chuyển, nhả đơn quá hạn, chỉ mục tìm kiếm AI.

Ứng dụng desktop lên lịch các tác vụ này bằng `view/_sync.py` (vòng `after` của Tk); ứng dụng web dùng luồng nền.
Chỉ `fetch_tracking` an toàn ở luồng phụ (chỉ gọi gateway); các hàm khác đọc / ghi CSDL.
"""
from __future__ import annotations

import logging

from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.search_engine import SearchEngine
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.controller import _flows
from abc_fashion.model.customer_data import NotificationEvent
from abc_fashion.model.fulfilment import order_status_from_shipments, Shipment, ShipmentEvent
from abc_fashion.model.sales import (PENDING_PAYMENT_TIMEOUT_MINUTES, OrderStatus, PaymentMethodType, PaymentStatus,
                                     can_transition, Order)

log = logging.getLogger("abc_fashion")


def _path_to(current: OrderStatus, target: OrderStatus) -> list[OrderStatus]:
    """Các bước hợp lệ (theo ORDER_NEXT) từ `current` tới `target`; rỗng nếu không đi được."""
    if can_transition(current, target):
        return [target]
    if can_transition(current, OrderStatus.SHIPPED) and can_transition(OrderStatus.SHIPPED, target):
        return [OrderStatus.SHIPPED, target]
    return []


class SyncController:
    def __init__(self):
        self.order_dao = OrderDAO()
        self.shipment_dao = ShipmentDAO()
        self.payment_dao = PaymentDAO()
        self.notification_dao = NotificationDAO()
        self.style_dao = StyleDAO()
        self.shipping_gateway = ShippingGateway()
        self.notification_gateway = NotificationGateway()
        self.search_engine = SearchEngine()

    def release_expired_orders(self) -> int:
        """Mục 9.5: huỷ đơn chờ thanh toán quá hạn để nhả hàng; trả số đơn đã huỷ."""
        return self.order_dao._cancel_expired_pending(PENDING_PAYMENT_TIMEOUT_MINUTES)

    def get_open_shipments(self) -> list[Shipment]:
        """Kiện đã có vận đơn và chưa kết thúc."""
        return self.shipment_dao._get_open_shipments()

    def fetch_tracking(self, shipments: list[Shipment]) -> list[tuple[Shipment, list[ShipmentEvent]]]:
        """Hỏi hãng vận chuyển từng kiện (bỏ qua kiện hãng không trả lời). An toàn ở luồng phụ."""
        results = []
        for s in shipments:
            try:
                results.append((s, self.shipping_gateway.get_tracking(s)))
            except Exception:                           # noqa: BLE001 - hãng không phản hồi: bỏ qua lần này
                log.warning("ShipmentSync: không hỏi được kiện %s", s.tracking_no)
        return results

    def apply_tracking(self, results: list[tuple[Shipment, list[ShipmentEvent]]]) -> set[int]:
        """Ghi sự kiện mới; với mỗi đơn có kiện đổi trạng thái, suy ra trạng thái đơn từ các kiện và đi từng bước hợp
        lệ; giao xong thì thu COD và báo khách. Trả id các đơn đã chạm tới."""
        touched: set[int] = set()
        for shipment, events in results:
            for e in sorted(events, key=lambda x: x.occurred_at):
                if self.shipment_dao.add_shipment_event(e, shipment) and shipment.returnRequestId is None:
                    touched.add(shipment.orderId)
        for order_id in touched:
            self._sync_order(order_id)
        return touched

    def _sync_order(self, order_id: int) -> None:
        order = self.order_dao._get_brief(order_id)
        target = order_status_from_shipments(self.shipment_dao.get_shipment_by_order(Order(id=order_id)))
        if order is None or target is None or target == order.status:
            return
        for step in _path_to(order.status, target):
            order.status = step
            if not self.order_dao.update_order_status(order):
                return
        if target == OrderStatus.DELIVERED:
            for p in self.payment_dao.get_payment_by_order(order):
                if p.method == PaymentMethodType.COD and p.status == PaymentStatus.PENDING:
                    p.status, p.transaction_ref = PaymentStatus.SUCCEEDED, f"COD-{order.order_no}"
                    self.payment_dao.update_payment(p)
            _flows.notify_customer(self, order.customerId, NotificationEvent.ORDER_DELIVERED,
                                   f"Đơn {order.order_no} đã giao thành công.")

    def push_search_index(self) -> None:
        """Đẩy danh mục sản phẩm lên dịch vụ AI (chỉ chế độ http; gửi ở luồng phụ)."""
        _flows.push_search_index(self.style_dao, self.search_engine)
