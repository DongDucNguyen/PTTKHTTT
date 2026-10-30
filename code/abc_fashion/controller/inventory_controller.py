"""InventoryController — tồn kho, điều chỉnh tồn, sổ kho, phiếu nhập hàng với nhà cung cấp (UC17, FR23)."""
from __future__ import annotations

import logging
from datetime import date

from abc_fashion.control.dao.audit_log_entry_dao import AuditLogEntryDAO
from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.control.dao.restock_request_dao import RestockRequestDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.stock_location_dao import StockLocationDAO
from abc_fashion.control.dao.stock_movement_dao import StockMovementDAO
from abc_fashion.control.dao.supplier_dao import SupplierDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.controller._errors import AccessDenied, BusinessError
from abc_fashion.model.audit import AuditAction, AuditLogEntry
from abc_fashion.model.catalogue import ProductVariant
from abc_fashion.model.customer_data import Channel, NotificationEvent, Notification
from abc_fashion.model.inventory import (MovementReason, RestockStatus, RestockItem, RestockRequest, StockLevel,
                                         StockLocation, StockMovement)
from abc_fashion.model.user import StaffMember, Supplier

log = logging.getLogger("abc_fashion")


class _Rollback(Exception):
    pass


class InventoryController:
    def __init__(self):
        self.stock_level_dao = StockLevelDAO()
        self.stock_location_dao = StockLocationDAO()
        self.stock_movement_dao = StockMovementDAO()
        self.product_variant_dao = ProductVariantDAO()
        self.restock_request_dao = RestockRequestDAO()
        self.supplier_dao = SupplierDAO()
        self.audit_log_entry_dao = AuditLogEntryDAO()
        self.notification_gateway = NotificationGateway()

    # ---------- tồn kho ----------
    def get_stock_locations(self) -> list[StockLocation]:
        return self.stock_location_dao.get_all_stock_location()

    def search_stock_level(self, location: StockLocation | None, key: str, below_reorder_point: bool) -> list[StockLevel]:
        return self.stock_level_dao.search_stock_level(location, key or "", bool(below_reorder_point))

    def adjust_stock(self, staff: StaffMember, stock_level: StockLevel, change: int, reference: str,
                     note: str) -> int:
        """FR23: điều chỉnh tồn có tham chiếu + lý do; tồn + sổ kho + nhật ký trong một transaction.
        Trả tồn thực trước khi điều chỉnh."""
        l = stock_level
        reference, note = (reference or "").strip(), (note or "").strip()
        if not change:
            raise BusinessError("Số thay đổi phải khác 0")
        if l.on_hand + change < l.reserved:
            raise BusinessError(f"Tồn sau điều chỉnh ({l.on_hand + change}) không được nhỏ hơn số đang giữ ({l.reserved})")
        if not reference or not note:
            raise BusinessError("Tham chiếu và lý do là bắt buộc")
        movement = StockMovement(quantity_change=change, reason=MovementReason.ADJUSTMENT, reference=reference,
                                 note=note, productVariantId=l.productVariantId, stockLocationId=l.stockLocationId,
                                 staffMemberId=staff.id)
        before = l.on_hand
        try:
            with self.stock_level_dao.con.transaction():
                if not self.stock_level_dao.adjust_stock(l, movement):
                    raise _Rollback()
                self.audit_log_entry_dao.add_audit_log_entry(
                    AuditLogEntry(entity=f"tblStockLevel#{l.id}", action=AuditAction.ADJUST_STOCK,
                                  changes=f"{l.sku}: on_hand {before} -> {l.on_hand} ({change:+d}); {reference}; {note}"),
                    staff)
        except _Rollback:
            raise BusinessError("Tồn kho vừa thay đổi, không điều chỉnh được. Vui lòng tải lại.") from None
        return before

    def get_movements(self, variant: ProductVariant, start: date, end: date,
                      reason: MovementReason | None) -> list[StockMovement]:
        if start > end:
            raise BusinessError("Ngày bắt đầu phải trước ngày kết thúc")
        return self.stock_movement_dao.get_movement_by_variant(variant, start, end, reason)

    def search_variant(self, key: str) -> list[ProductVariant]:
        return self.product_variant_dao.search_variant(key or "")

    # ---------- phiếu nhập hàng (kho) ----------
    def get_suppliers(self) -> list[Supplier]:
        return self.supplier_dao.get_all_supplier()

    def search_restock_request(self, status: RestockStatus | None, supplier: Supplier | None) -> list[RestockRequest]:
        return self.restock_request_dao.search_restock_request(status, supplier)

    def get_restock_request_detail(self, restock_request: RestockRequest | None) -> RestockRequest:
        """Phiếu đầy đủ (kèm `items`); None → phiếu nháp mới."""
        if restock_request is None:
            r = RestockRequest(status=RestockStatus.DRAFT)
            r.items = []
            return r
        return self.restock_request_dao.get_restock_request_detail(restock_request)

    @staticmethod
    def add_restock_item(restock_request: RestockRequest, variant: ProductVariant, quantity: int,
                         location: StockLocation | None) -> RestockRequest:
        """Thêm (cộng dồn) một biến thể vào phiếu chưa lưu; mỗi biến thể chỉ nhập vào kho của nó."""
        if (quantity or 0) <= 0:
            raise BusinessError("Số lượng phải > 0")
        if location and getattr(variant, "stockLocationId", None) not in (None, location.id):
            raise BusinessError(f"{variant.sku} thuộc {getattr(variant, 'location_name', 'kho khác')}; "
                                f"mỗi biến thể chỉ nhập vào kho của nó")
        for i in restock_request.items:
            if i.productVariantId == variant.id:
                i.quantity += quantity
                break
        else:
            item = RestockItem(productVariantId=variant.id, quantity=quantity)
            item.sku, item.colour, item.size_label = variant.sku, variant.colour, variant.size_label
            item.style_name = getattr(variant, "style_name", "")
            restock_request.items.append(item)
        return restock_request

    def save_restock_request(self, staff: StaffMember, restock_request: RestockRequest, supplier: Supplier | None,
                             location: StockLocation | None, expected_date: date, send: bool) -> bool:
        """Lưu nháp (`send=False`) hoặc gửi nhà cung cấp (`send=True`, kèm e-mail báo phiếu chờ xác nhận)."""
        r = restock_request
        if supplier is None or location is None or not r.items:
            raise BusinessError("Chọn nhà cung cấp, kho và thêm ít nhất một dòng")
        r.supplierId, r.stockLocationId = supplier.id, location.id
        r.status = RestockStatus.SENT if send else RestockStatus.DRAFT
        r.expected_date = expected_date
        ok = (self.restock_request_dao.update_restock_request(r) if r.id
              else self.restock_request_dao.add_restock_request(r, staff))
        if not ok:
            r.status = RestockStatus.DRAFT
            raise BusinessError("Không lưu được phiếu (phiếu đã được gửi hoặc dữ liệu không hợp lệ)")
        if send:
            try:                                           # e-mail cho nhà cung cấp (không lưu Notification)
                mail = Notification(channel=Channel.EMAIL, event_type=NotificationEvent.ORDER_CONFIRMED,
                                    message=f"Phiếu nhập {r.request_no} đang chờ bạn xác nhận.")
                mail.recipient = supplier.email
                self.notification_gateway.send(mail)
            except Exception:                              # noqa: BLE001 - lỗi gửi không chặn nghiệp vụ
                log.exception("notify supplier")
        return True

    def receive_restock(self, staff: StaffMember, restock_request: RestockRequest) -> int:
        """Nhận đủ hàng của phiếu đã được nhà cung cấp xác nhận: cộng tồn + sổ kho. Trả tổng số sản phẩm."""
        if restock_request.status != RestockStatus.CONFIRMED:
            raise BusinessError("Chỉ nhận hàng với phiếu đã được nhà cung cấp xác nhận")
        r = self.restock_request_dao.get_restock_request_detail(restock_request)
        if not self.restock_request_dao.receive_restock_request(r, staff):
            raise BusinessError("Không nhận được: phiếu đã đổi trạng thái hoặc có biến thể thuộc kho khác")
        return sum(i.quantity for i in r.items)

    # ---------- nhà cung cấp ----------
    def get_supplier_restock(self, supplier: Supplier, restock_request: RestockRequest) -> RestockRequest:
        r = self.restock_request_dao.get_restock_request_detail(restock_request)
        if r.supplierId != supplier.id:
            raise AccessDenied("Phiếu này không gửi cho bạn")
        return r

    def confirm_restock(self, supplier: Supplier, restock_request: RestockRequest, expected_date: date,
                        note: str) -> bool:
        if expected_date < date.today():
            raise BusinessError("Ngày giao dự kiến không được trước hôm nay")
        r = restock_request
        if r.supplierId != supplier.id:
            raise AccessDenied("Phiếu này không gửi cho bạn")
        r.status, r.confirm_at, r.expected_date = RestockStatus.CONFIRMED, date.today(), expected_date
        r.supplier_note = (note or "").strip() or None
        if not self.restock_request_dao.update_restock_request(r):
            raise BusinessError("Phiếu vừa thay đổi trạng thái, vui lòng mở lại")
        return True

    def refuse_restock(self, supplier: Supplier, restock_request: RestockRequest, note: str) -> bool:
        note = (note or "").strip()
        if not note:
            raise BusinessError("Nhập lý do từ chối")                                       # UC17 E1
        r = restock_request
        if r.supplierId != supplier.id:
            raise AccessDenied("Phiếu này không gửi cho bạn")
        r.status, r.supplier_note = RestockStatus.CANCELLED, note
        if not self.restock_request_dao.update_restock_request(r):
            raise BusinessError("Phiếu vừa thay đổi trạng thái, vui lòng mở lại")
        return True
