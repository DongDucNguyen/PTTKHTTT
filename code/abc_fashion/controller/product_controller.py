"""ProductController — quản lý sản phẩm: style, vật liệu, bảng cỡ, ảnh / video, biến thể (UC21).

Sau mỗi thay đổi sản phẩm / biến thể / ảnh, chỉ mục tìm kiếm của dịch vụ AI được đẩy lại (chỉ ở chế độ http).
"""
from __future__ import annotations

from abc_fashion.control.dao.audit_log_entry_dao import AuditLogEntryDAO
from abc_fashion.control.dao.category_dao import CategoryDAO
from abc_fashion.control.dao.collection_dao import CollectionDAO
from abc_fashion.control.dao.material_component_dao import MaterialComponentDAO
from abc_fashion.control.dao.product_media_dao import ProductMediaDAO
from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.control.dao.size_chart_entry_dao import SizeChartEntryDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.stock_location_dao import StockLocationDAO
from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.control.dao.supplier_dao import SupplierDAO
from abc_fashion.control.gateway.search_engine import SearchEngine
from abc_fashion.controller import _flows
from abc_fashion.controller._errors import BusinessError
from abc_fashion.controller._media import delete_media_file, save_media
from abc_fashion.model.audit import AuditAction, AuditLogEntry
from abc_fashion.model.catalogue import (MediaType, Measure, StyleStatus, category_descendants, Category, Collection,
                                         MaterialComponent, ProductMedia, ProductVariant, SizeChartEntry, Style)
from abc_fashion.model.inventory import StockLevel, StockLocation
from abc_fashion.model.user import StaffMember, Supplier

STYLE_FIELDS = ("code", "name", "description", "brand", "fit_type", "care_instructions", "features", "model_info",
                "status", "categoryId", "supplierId", "collectionId")


class _Rollback(Exception):
    pass


def _v(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


class ProductController:
    def __init__(self):
        self.style_dao = StyleDAO()
        self.category_dao = CategoryDAO()
        self.collection_dao = CollectionDAO()
        self.supplier_dao = SupplierDAO()
        self.product_media_dao = ProductMediaDAO()
        self.material_component_dao = MaterialComponentDAO()
        self.size_chart_entry_dao = SizeChartEntryDAO()
        self.product_variant_dao = ProductVariantDAO()
        self.stock_level_dao = StockLevelDAO()
        self.stock_location_dao = StockLocationDAO()
        self.audit_log_entry_dao = AuditLogEntryDAO()
        self.search_engine = SearchEngine()

    # ---------- danh mục tra cứu ----------
    def get_categories(self) -> list[Category]:
        return self.category_dao.get_all_category()

    def get_suppliers(self) -> list[Supplier]:
        return self.supplier_dao.get_all_supplier()

    def get_collections(self) -> list[Collection]:
        return self.collection_dao.get_all_collection()

    def get_stock_locations(self) -> list[StockLocation]:
        return self.stock_location_dao.get_all_stock_location()

    def _refresh_index(self) -> None:
        _flows.push_search_index(self.style_dao, self.search_engine)

    # ---------- danh sách ----------
    def search_style(self, key: str, category: Category | None, status: StyleStatus | None) -> list[Style]:
        """Mọi trạng thái; lọc theo danh mục (gồm danh mục con) và trạng thái."""
        styles = self.style_dao.search_style(key or "")
        if category is not None:
            ids = category_descendants(self.category_dao.get_all_category(), category.id)
            styles = [s for s in styles if s.categoryId in ids]
        if status is not None:
            styles = [s for s in styles if s.status == status]
        return styles

    def deactivate_style(self, staff: StaffMember, style: Style) -> bool:
        """Ngừng bán style và mọi biến thể (cùng nhật ký trong một transaction)."""
        if style.status == StyleStatus.INACTIVE:
            return False
        with self.style_dao.con.transaction():
            ok = self.style_dao.deactivate_style(style)
            if ok:
                self.audit_log_entry_dao.add_audit_log_entry(
                    AuditLogEntry(entity=f"tblStyle#{style.id}", action=AuditAction.DEACTIVATE,
                                  changes="status -> inactive; variants -> discontinued"), staff)
        self._refresh_index()
        return ok

    # ---------- sửa style ----------
    def get_style_for_edit(self, style: Style) -> Style:
        """Style mới (chưa có id) giữ nguyên; style có sẵn được nạp lại, gắn động `materials`, `size_chart`, `media`,
        `variants` (mọi trạng thái, kèm kho và số có thể bán)."""
        if not style.id:
            style.materials, style.size_chart, style.media, style.variants = [], [], [], []
            return style
        s = self.style_dao.get_style_detail(style)
        s.materials = self.material_component_dao.get_material_by_style(s)
        s.size_chart = self.size_chart_entry_dao.get_size_chart_by_style(s)
        s.media = self.product_media_dao.get_media_by_style(s)
        s.variants = self.product_variant_dao.get_variant_by_style(s)
        return s

    @staticmethod
    def make_material(material: str, percent: int) -> MaterialComponent:
        material = (material or "").strip()
        if not material or not (1 <= (percent or 0) <= 100):
            raise BusinessError("Nhập tên vật liệu và phần trăm 1–100")
        return MaterialComponent(material=material, percent=percent)

    @staticmethod
    def make_size_entry(size_label: str, measure: Measure | None, value_cm: float | None) -> SizeChartEntry:
        size_label = (size_label or "").strip()
        if not size_label or measure is None or not value_cm or value_cm <= 0:
            raise BusinessError("Nhập cỡ, số đo và giá trị cm > 0")
        return SizeChartEntry(size_label=size_label, measure=measure, value_cm=value_cm)

    def save_style(self, staff: StaffMember, style: Style, draft: Style, materials: list[MaterialComponent],
                   size_chart: list[SizeChartEntry]) -> bool:
        """Lưu style (các trường STYLE_FIELDS lấy từ `draft`) + vật liệu + bảng cỡ + nhật ký trong một transaction.

        Muốn chuyển sang Đang bán cần vật liệu đủ 100% và ít nhất một biến thể đang bán. Lỗi → BusinessError và
        `style` giữ nguyên như trước khi lưu."""
        if not (draft.code and draft.name and draft.categoryId and draft.supplierId):
            raise BusinessError("Nhập mã, tên, danh mục, nhà cung cấp")
        total = sum(x.percent for x in materials)
        if materials and total != 100:
            raise BusinessError(f"Tổng thành phần vật liệu phải bằng 100% (hiện {total}%)")
        desired = draft.status or StyleStatus.DRAFT
        if desired == StyleStatus.ACTIVE and total != 100:
            raise BusinessError("Muốn bán (active) cần thành phần vật liệu đủ 100%")
        s, old = style, {k: getattr(style, k) for k in STYLE_FIELDS}
        is_new = s.id is None
        for k in STYLE_FIELDS:
            setattr(s, k, getattr(draft, k))
        try:
            with self.style_dao.con.transaction():
                s.status = StyleStatus.DRAFT if desired == StyleStatus.ACTIVE else desired
                if not (self.style_dao.add_style(s) if is_new else self.style_dao.update_style(s)):
                    raise _Rollback("Mã sản phẩm đã tồn tại hoặc dữ liệu không hợp lệ")
                if not self.material_component_dao.save_material(s, materials):
                    raise _Rollback("Thành phần vật liệu không hợp lệ")
                if not self.size_chart_entry_dao.save_size_chart(s, size_chart):
                    raise _Rollback("Bảng cỡ không hợp lệ")
                if desired == StyleStatus.ACTIVE:
                    s.status = StyleStatus.ACTIVE
                    if not self.style_dao.update_style(s):
                        raise _Rollback("Muốn bán (active) cần vật liệu đủ 100% và ít nhất một biến thể đang bán")
                changes = "; ".join(f"{k}: {_v(old[k])} -> {_v(getattr(s, k))}" for k in STYLE_FIELDS
                                    if old[k] != getattr(s, k)) or "vật liệu / bảng cỡ"
                self.audit_log_entry_dao.add_audit_log_entry(
                    AuditLogEntry(entity=f"tblStyle#{s.id}", action=AuditAction.CREATE if is_new else AuditAction.UPDATE,
                                  changes=changes), staff)
        except _Rollback as e:
            for k, value in old.items():
                setattr(s, k, value)
            if is_new:
                s.id = None
            raise BusinessError(str(e)) from None
        self._refresh_index()
        return True

    # ---------- ảnh / video ----------
    def upload_media(self, style: Style, file_name: str, data: bytes) -> ProductMedia:
        if not style.id:
            raise BusinessError("Lưu sản phẩm trước khi tải ảnh lên")
        kind = MediaType.VIDEO if file_name.lower().endswith((".mp4", ".mov")) else MediaType.IMAGE
        media = ProductMedia(url=save_media(file_name, data, "products"), media_type=kind)
        if not self.product_media_dao.add_media(media, style):
            delete_media_file(media.url, "products")
            raise BusinessError("Không lưu được ảnh / video")
        self._refresh_index()
        return media

    def delete_media(self, media: ProductMedia) -> bool:
        ok = self.product_media_dao.delete_media(media)
        if ok:
            delete_media_file(media.url, "products")
            self._refresh_index()
        return ok

    def get_media(self, style: Style) -> list[ProductMedia]:
        return self.product_media_dao.get_media_by_style(style)

    # ---------- biến thể ----------
    def get_variants(self, style: Style) -> list[ProductVariant]:
        return self.product_variant_dao.get_variant_by_style(style)

    def save_variant(self, style: Style, variant: ProductVariant, location: StockLocation | None,
                     reorder_point: int) -> bool:
        """Thêm (`variant.id` rỗng: cùng bản ghi tồn kho đầu tiên ở `location`, một transaction) hoặc sửa biến thể."""
        v = variant
        v.sku, v.size_label, v.colour = (v.sku or "").strip(), (v.size_label or "").strip(), (v.colour or "").strip()
        if not (v.sku and v.size_label and v.colour):
            raise BusinessError("Nhập SKU, cỡ, màu")
        if not v.price or v.price <= 0:
            raise BusinessError("Giá phải là số nguyên dương")
        if v.id:
            if not self.product_variant_dao.update_variant(v):
                raise BusinessError("Trùng SKU hoặc trùng cỡ + màu với biến thể khác")
        else:
            if location is None:
                raise BusinessError("Chọn kho cho biến thể mới")
            v.styleId = style.id
            try:
                with self.product_variant_dao.con.transaction():
                    if not self.product_variant_dao.add_variant(v, style):
                        raise _Rollback("Trùng SKU hoặc trùng cỡ + màu với biến thể khác")
                    if not self.stock_level_dao.add_stock_level(StockLevel(reorder_point=reorder_point or 0), v,
                                                                location):
                        raise _Rollback("Không tạo được bản ghi tồn kho")
            except _Rollback as e:
                v.id = None
                raise BusinessError(str(e)) from None
        self._refresh_index()
        return True
