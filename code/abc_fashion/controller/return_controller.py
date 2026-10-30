"""ReturnController — trả / đổi hàng: khách gửi yêu cầu (UC14), CSKH xử lý (UC18), kho kiểm tra hàng trả về."""
from __future__ import annotations

import os
from datetime import datetime

from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.controller import _flows
from abc_fashion.controller._errors import AccessDenied, BusinessError
from abc_fashion.controller._media import save_media
from abc_fashion.model.catalogue import MediaType, VariantStatus, ProductVariant, Style
from abc_fashion.model.customer_data import NotificationEvent
from abc_fashion.model.fulfilment import ShipmentDirection, ShipmentStatus, Shipment, ShipmentRecord
from abc_fashion.model.inventory import MovementReason, StockLevel, StockMovement
from abc_fashion.model.returns import (EVIDENCE_REQUIRED, InspectionResult, Resolution, ReturnStatus, ReturnType,
                                       refund_amount, within_return_window, ReturnEvidence, ReturnItem, ReturnRequest)
from abc_fashion.model.sales import DeliveryService, Order, OrderItem
from abc_fashion.model.user import Customer, StaffMember

VIDEO_EXT = (".mp4", ".mov", ".avi", ".mkv")


class _Rollback(Exception):
    pass


class ReturnController:
    def __init__(self):
        self.return_request_dao = ReturnRequestDAO()
        self.product_variant_dao = ProductVariantDAO()
        self.shipment_dao = ShipmentDAO()
        self.payment_dao = PaymentDAO()
        self.stock_level_dao = StockLevelDAO()
        self.notification_dao = NotificationDAO()
        self.payment_gateway = PaymentGateway()
        self.shipping_gateway = ShippingGateway()
        self.notification_gateway = NotificationGateway()

    # ====================================================================== khách (UC14)
    def get_replacement_options(self, order_item: OrderItem) -> list[ProductVariant]:
        """Biến thể cùng style (đang bán, khác biến thể đã mua) để đổi sang; gắn `available`."""
        return [v for v in self.product_variant_dao.get_variant_by_style(Style(id=order_item.styleId))
                if v.id != order_item.productVariantId and v.status == VariantStatus.ACTIVE]

    def make_return_item(self, order_item: OrderItem, quantity: int, return_type: ReturnType,
                         replacement: ProductVariant | None) -> ReturnItem:
        """Một dòng của yêu cầu (chưa lưu). Đổi hàng thì bắt buộc chọn biến thể thay thế."""
        if not (0 < (quantity or 0) <= order_item.quantity):
            raise BusinessError(f"Số lượng trả từ 1 đến {order_item.quantity}")
        if return_type == ReturnType.EXCHANGE and replacement is None:
            raise BusinessError("Chọn màu / cỡ muốn đổi sang")
        if return_type != ReturnType.EXCHANGE:
            replacement = None
        ri = ReturnItem(orderItemId=order_item.id, quantity=quantity, sku=order_item.sku,
                        replacementVariantId=replacement.id if replacement else None)
        ri.replacement_label = f"{replacement.colour}/{replacement.size_label}" if replacement else ""
        return ri

    def store_evidence(self, file_name: str, data: bytes) -> ReturnEvidence:
        """Lưu ảnh / video bằng chứng vào media/returns; trả ReturnEvidence chưa gắn vào yêu cầu."""
        if not data:
            raise BusinessError("File bằng chứng rỗng")
        kind = MediaType.VIDEO if file_name.lower().endswith(VIDEO_EXT) else MediaType.IMAGE
        e = ReturnEvidence(url=save_media(file_name, data, "returns"), media_type=kind)
        e.file_name = os.path.basename(file_name)
        return e

    def submit_return_request(self, customer: Customer, order: Order, return_request: ReturnRequest,
                              evidence: list[ReturnEvidence]) -> ReturnRequest:
        """Gửi yêu cầu (`items`, `return_type`, `desired_resolution`, `reason_code`, `reason_detail` đã đặt)."""
        rr = return_request
        if order.customerId != customer.id:
            raise AccessDenied("Bạn không thao tác được trên đơn hàng này")
        if not getattr(rr, "items", None):
            raise BusinessError("Thêm ít nhất một dòng hàng vào yêu cầu")
        if rr.reason_code is None:
            raise BusinessError("Chọn lý do")
        if rr.reason_code in EVIDENCE_REQUIRED and not evidence:
            raise BusinessError("Lỗi sản phẩm / sai hàng / không như mô tả cần ảnh hoặc video bằng chứng")
        if rr.return_type == ReturnType.EXCHANGE and any(i.replacementVariantId is None for i in rr.items):
            raise BusinessError("Mỗi dòng đổi hàng cần chọn màu / cỡ thay thế")
        rr.desired_resolution = rr.desired_resolution or (
            Resolution.EXCHANGE if rr.return_type == ReturnType.EXCHANGE else Resolution.REFUND)
        rr.reason_detail = (rr.reason_detail or "").strip() or None
        rr.orderId = order.id
        for e in evidence:
            e.id = None
        rr.evidence = list(evidence)
        if not self.return_request_dao.add_return_request(rr, order):
            raise BusinessError("Không gửi được: đơn đã có yêu cầu trả, đã quá hạn trả hoặc số lượng không hợp lệ")
        return rr

    # ====================================================================== nhân viên (UC18)
    def search_return_request(self, key: str, status: ReturnStatus | None) -> list[ReturnRequest]:
        return self.return_request_dao.search_return_request(key or "", status)

    def get_return_request_detail(self, return_request: ReturnRequest) -> ReturnRequest:
        """Yêu cầu đầy đủ (items, evidence, shipments) — gắn động `can_authorise`, `can_reject`, `can_create_pickup`,
        `can_refund`, `can_ship_replacement`, `can_close`, `can_inspect` theo trạng thái."""
        r = self.return_request_dao.get_return_request_detail(return_request)
        st = r.status
        exchange = r.return_type == ReturnType.EXCHANGE or r.desired_resolution == Resolution.EXCHANGE
        r.can_authorise = r.can_reject = st == ReturnStatus.REQUESTED
        r.can_create_pickup = st == ReturnStatus.AUTHORISED
        r.can_refund = st == ReturnStatus.INSPECTED
        r.can_ship_replacement = st == ReturnStatus.INSPECTED and exchange
        r.can_close = st in (ReturnStatus.REFUNDED, ReturnStatus.EXCHANGED, ReturnStatus.REJECTED)
        r.can_inspect = st == ReturnStatus.IN_TRANSIT
        return r

    def _set_status(self, staff: StaffMember, r: ReturnRequest, status: ReturnStatus, note: str | None = None) -> None:
        old = r.status
        r.status, r.decision_note = status, note
        if not self.return_request_dao.update_return_request(r, staff):
            r.status = old
            raise BusinessError("Yêu cầu vừa được người khác cập nhật")

    def _notify(self, r: ReturnRequest, event: NotificationEvent, message: str) -> None:
        _flows.notify_customer(self, r.customerId, event, message)

    @staticmethod
    def _order(r: ReturnRequest) -> Order:
        return Order(id=r.orderId, order_no=getattr(r, "order_no", None), customerId=r.customerId)

    def authorise(self, staff: StaffMember, return_request: ReturnRequest, note: str) -> bool:
        """Duyệt yêu cầu. Quá hạn trả hàng (UC18 E2) → tự từ chối và trả False."""
        r = return_request
        if not within_return_window(getattr(r, "delivered_at", None), datetime.now()):
            self._set_status(staff, r, ReturnStatus.REJECTED, "Quá hạn trả hàng")
            self._notify(r, NotificationEvent.RETURN_REJECTED, f"Yêu cầu {r.return_no} bị từ chối: quá hạn trả hàng.")
            return False
        self._set_status(staff, r, ReturnStatus.AUTHORISED, (note or "").strip() or None)
        self._notify(r, NotificationEvent.RETURN_AUTHORISED,
                     f"Yêu cầu {r.return_no} đã được duyệt. Hãng vận chuyển sẽ đến lấy hàng.")
        return True

    def reject(self, staff: StaffMember, return_request: ReturnRequest, note: str) -> bool:
        note = (note or "").strip()
        if not note:
            raise BusinessError("Nhập lý do từ chối")
        self._set_status(staff, return_request, ReturnStatus.REJECTED, note)
        self._notify(return_request, NotificationEvent.RETURN_REJECTED,
                     f"Yêu cầu {return_request.return_no} bị từ chối: {note}")
        return True

    def _not_handed_over(self, r: ReturnRequest, direction: ShipmentDirection) -> list[Shipment]:
        """Kiện của yêu cầu đã tạo trong CSDL nhưng chưa bàn giao được cho hãng (chưa có vận đơn)."""
        return [s for s in getattr(r, "shipments", [])
                if s.direction == direction and s.status == ShipmentStatus.REQUESTED and not s.tracking_no]

    def create_pickup(self, staff: StaffMember, return_request: ReturnRequest) -> Shipment:
        """Tạo kiện lấy hàng và bàn giao cho hãng. Lần trước hãng không phản hồi → dùng lại kiện đã tạo."""
        r = return_request
        pending = self._not_handed_over(r, ShipmentDirection.RETURN)
        if pending:
            shipment = pending[0]
        else:
            location_id = next((i.stockLocationId for i in r.items if i.stockLocationId), None)
            shipment = Shipment(direction=ShipmentDirection.RETURN, service_level=DeliveryService.STANDARD, fee=0,
                                status=ShipmentStatus.REQUESTED, stockLocationId=location_id, returnRequestId=r.id)
            shipment.records = [ShipmentRecord(quantity=i.quantity, orderItemId=i.orderItemId) for i in r.items]
            if not self.shipment_dao.add_shipment(shipment, self._order(r)):
                raise BusinessError("Không tạo được kiện lấy hàng")
        shipment.from_location, shipment.to_address = getattr(r, "ship_address", "") or "", "Kho ABC Fashion"
        shipment.carrier, shipment.tracking_no = self.shipping_gateway.create_shipment(shipment)
        shipment.status = ShipmentStatus.PICKED_UP
        self.shipment_dao.update_shipment(shipment)
        self._set_status(staff, r, ReturnStatus.IN_TRANSIT)
        return shipment

    def refund(self, staff: StaffMember, return_request: ReturnRequest, note: str) -> int:
        """Hoàn tiền các dòng đạt kiểm tra (`refund_amount`); không dòng nào đạt → đánh dấu đã xử lý, hoàn 0 đ."""
        r = return_request
        amount = refund_amount(r.items)
        if amount <= 0:
            self._set_status(staff, r, ReturnStatus.REFUNDED, "Không hoàn tiền: hàng không đạt kiểm tra")
            return 0
        ok, refunded = _flows.refund_order(self, self._order(r), amount)
        if not ok:
            raise BusinessError("Cổng thanh toán từ chối hoàn tiền hoặc đơn không còn tiền để hoàn")
        self._set_status(staff, r, ReturnStatus.REFUNDED, (note or "").strip() or f"Đã hoàn {_flows.money(refunded)}")
        self._notify(r, NotificationEvent.REFUND_COMPLETED, f"Đã hoàn {_flows.money(refunded)} cho yêu cầu {r.return_no}.")
        return refunded

    def ship_replacement(self, staff: StaffMember, return_request: ReturnRequest, note: str) -> list[Shipment]:
        """Trừ kho biến thể thay thế + tạo kiện đổi (một transaction), rồi bàn giao cho hãng. Lần trước hãng không
        phản hồi (kho đã trừ, kiện đã tạo) → chỉ bàn giao lại các kiện đó, không trừ kho lần hai."""
        r = return_request
        lines = [i for i in r.items if i.inspection_result == InspectionResult.PASSED and i.replacementVariantId]
        if not lines:
            raise BusinessError("Không có dòng đạt kiểm tra cần đổi — hãy hoàn tiền")
        shipments: dict[int, Shipment] = {s.id: s for s in self._not_handed_over(r, ShipmentDirection.OUTBOUND)}
        if not shipments:
            levels = {i.id: self.stock_level_dao.get_stock_level_by_variant(ProductVariant(id=i.replacementVariantId))
                      for i in lines}
            short = [i.replacement_sku for i in lines if levels[i.id] is None or levels[i.id].available < i.quantity]
            if short:                                                                         # A1
                raise BusinessError(f"Hết hàng để đổi: {', '.join(short)}. Đề nghị khách nhận hoàn tiền.")
            try:
                with self.stock_level_dao.con.transaction():                       # trừ kho + tạo kiện đổi
                    for i in sorted(lines, key=lambda x: x.replacementVariantId):
                        level = levels[i.id]
                        if not self.stock_level_dao.adjust_stock(level, StockMovement(
                                quantity_change=-i.quantity, reason=MovementReason.SALE, reference=r.return_no,
                                note="Gửi hàng đổi", staffMemberId=staff.id)):
                            raise _Rollback()
                        s = shipments.setdefault(level.stockLocationId, Shipment(
                            direction=ShipmentDirection.OUTBOUND, service_level=DeliveryService.STANDARD, fee=0,
                            status=ShipmentStatus.REQUESTED, stockLocationId=level.stockLocationId, returnRequestId=r.id))
                        s.records = getattr(s, "records", []) + [ShipmentRecord(quantity=i.quantity,
                                                                                orderItemId=i.orderItemId)]
                    for s in shipments.values():
                        if not self.shipment_dao.add_shipment(s, self._order(r)):
                            raise _Rollback()
            except _Rollback:
                raise BusinessError("Tồn kho vừa thay đổi, không gửi được hàng đổi") from None
        for s in shipments.values():                                          # gọi hãng sau khi commit
            s.from_location, s.to_address = "Kho ABC Fashion", getattr(r, "ship_address", "") or ""
            s.carrier, s.tracking_no = self.shipping_gateway.create_shipment(s)
            s.status = ShipmentStatus.PICKED_UP
            self.shipment_dao.update_shipment(s)
        self._set_status(staff, r, ReturnStatus.EXCHANGED, (note or "").strip() or None)
        self._notify(r, NotificationEvent.EXCHANGE_SHIPPED, f"Hàng đổi cho yêu cầu {r.return_no} đã được gửi: "
                     + ", ".join(s.tracking_no for s in shipments.values()))
        return list(shipments.values())

    def close(self, staff: StaffMember, return_request: ReturnRequest, note: str) -> bool:
        self._set_status(staff, return_request, ReturnStatus.CLOSED, (note or "").strip() or None)
        return True

    # ====================================================================== kho kiểm tra hàng trả về
    def save_inspection(self, item: ReturnItem, result: InspectionResult, note: str) -> bool:
        note = (note or "").strip()
        if result == InspectionResult.FAILED and not note:
            raise BusinessError("Ghi rõ lý do không đạt")
        item.inspection_result, item.inspection_note = result, note or None
        return self.return_request_dao.update_return_item(item)

    def finish_inspection(self, staff: StaffMember, return_request: ReturnRequest) -> int:
        """Nhập lại kho các dòng đạt (FR29), chuyển yêu cầu sang inspected, đánh dấu kiện lấy hàng đã về kho —
        cùng một transaction. Trả số sản phẩm đã nhập kho."""
        r = return_request
        if any(i.inspection_result == InspectionResult.PENDING for i in r.items):
            raise BusinessError("Còn dòng chưa kiểm tra")
        passed = [i for i in r.items if i.inspection_result == InspectionResult.PASSED]
        r.status = ReturnStatus.INSPECTED
        try:
            with self.return_request_dao.con.transaction():
                for i in sorted(passed, key=lambda x: x.productVariantId):
                    movement = StockMovement(quantity_change=i.quantity, reason=MovementReason.RETURN,
                                             reference=r.return_no, note="Hàng trả kiểm tra đạt", staffMemberId=staff.id)
                    if not self.stock_level_dao.adjust_stock(StockLevel(id=i.stock_level_id), movement):
                        raise _Rollback()
                if not self.return_request_dao.update_return_request(r, staff):
                    raise _Rollback()
                for s in getattr(r, "shipments", []):
                    if s.direction == ShipmentDirection.RETURN and s.status != ShipmentStatus.DELIVERED:
                        s.status = ShipmentStatus.DELIVERED
                        self.shipment_dao.update_shipment(s)
        except _Rollback:
            r.status = ReturnStatus.IN_TRANSIT
            raise BusinessError("Yêu cầu vừa được người khác cập nhật, vui lòng mở lại") from None
        return sum(i.quantity for i in passed)
