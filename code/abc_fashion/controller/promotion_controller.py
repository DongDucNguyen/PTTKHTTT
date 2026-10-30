"""PromotionController — chương trình khuyến mãi, style áp dụng, mã giảm giá (UC15, UC27)."""
from __future__ import annotations

from datetime import date, datetime, time

from abc_fashion.control.dao.category_dao import CategoryDAO
from abc_fashion.control.dao.promotion_dao import PromotionDAO
from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.control.dao.voucher_dao import VoucherDAO
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.catalogue import category_descendants, Category, Style
from abc_fashion.model.sales import DiscountType, PromoType, PromotionStatus, Promotion, Voucher


class PromotionController:
    def __init__(self):
        self.promotion_dao = PromotionDAO()
        self.voucher_dao = VoucherDAO()
        self.style_dao = StyleDAO()
        self.category_dao = CategoryDAO()

    def search_promotion(self, key: str, status: PromotionStatus | None) -> list[Promotion]:
        return self.promotion_dao.search_promotion(key or "", status)

    def get_promotion_detail(self, promotion: Promotion) -> Promotion:
        """Chương trình đầy đủ, gắn động `styles` và `vouchers`. Chương trình mới (chưa có id) giữ nguyên."""
        if not promotion.id:
            promotion.styles, promotion.vouchers = [], []
            return promotion
        p = self.promotion_dao.get_promotion_detail(promotion)
        p.vouchers = self.voucher_dao.get_voucher_by_promotion(p)
        return p

    def save_promotion(self, promotion: Promotion, name: str, promo_type: PromoType, discount_type: DiscountType,
                       discount_value: int | None, min_order_value: int | None, start: date, end: date,
                       status: PromotionStatus, styles: list[Style]) -> bool:
        """Thêm / sửa chương trình; kết thúc tính đến hết ngày `end`."""
        name = (name or "").strip()
        starts_at, ends_at = datetime.combine(start, time.min), datetime.combine(end, time(23, 59, 59))
        if not name:
            raise BusinessError("Nhập tên chương trình")
        if ends_at <= starts_at:
            raise BusinessError("Ngày kết thúc phải sau ngày bắt đầu")
        if (discount_value is None or discount_value <= 0
                or (discount_type == DiscountType.PERCENT and not 1 <= discount_value <= 100)):
            raise BusinessError("Giảm theo % phải từ 1–100; giảm tiền phải > 0")
        if min_order_value is None or min_order_value < 0:
            raise BusinessError("Đơn tối thiểu phải ≥ 0")
        p = promotion
        p.name, p.promo_type, p.discount_type, p.discount_value = name, promo_type, discount_type, discount_value
        p.min_order_value, p.starts_at, p.ends_at, p.status = min_order_value, starts_at, ends_at, status
        p.styles = list(styles)
        ok = self.promotion_dao.update_promotion(p) if p.id else self.promotion_dao.add_promotion(p)
        if not ok:
            raise BusinessError("Không lưu được chương trình")
        return True

    def end_promotion(self, promotion: Promotion) -> bool:
        """Kết thúc sớm; chương trình đã kết thúc thì trả False."""
        if promotion.status == PromotionStatus.ENDED:
            return False
        promotion.status = PromotionStatus.ENDED
        if not self.promotion_dao.update_promotion(promotion):
            raise BusinessError("Không cập nhật được chương trình")
        return True

    def add_voucher(self, promotion: Promotion, code: str, usage_limit: int) -> list[Voucher]:
        """Thêm mã giảm giá; trả danh sách mã của chương trình."""
        code = (code or "").strip()
        if not promotion.id:
            raise BusinessError("Lưu chương trình trước khi thêm mã")
        if not code or (usage_limit or 0) <= 0:
            raise BusinessError("Nhập mã và giới hạn lượt dùng > 0")
        if not self.voucher_dao.add_voucher(Voucher(code=code, usage_limit=usage_limit), promotion):
            raise BusinessError(f"Mã {code.upper()} đã tồn tại")
        return self.voucher_dao.get_voucher_by_promotion(promotion)

    # ---------- chọn style áp dụng ----------
    def get_categories(self) -> list[Category]:
        return self.category_dao.get_all_category()

    def search_style(self, key: str, category: Category | None) -> list[Style]:
        styles = self.style_dao.search_style(key or "")
        if category is not None:
            ids = category_descendants(self.category_dao.get_all_category(), category.id)
            styles = [s for s in styles if s.categoryId in ids]
        return styles
