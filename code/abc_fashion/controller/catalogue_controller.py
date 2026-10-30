"""CatalogueController — duyệt / tìm sản phẩm (UC04, UC05), trang chi tiết (UC06, UC33), trợ lý AI (UC32).

Hàm có ghi "an toàn ở luồng phụ" chỉ gọi gateway, không đụng CSDL (mục 11, quy tắc 6): view được gọi chúng
trong `run_in_thread`; mọi hàm khác chỉ gọi ở luồng giao diện / luồng của request.
"""
from __future__ import annotations

import logging

from abc_fashion.control.dao.assistant_turn_dao import AssistantTurnDAO
from abc_fashion.control.dao.category_dao import CategoryDAO
from abc_fashion.control.dao.material_component_dao import MaterialComponentDAO
from abc_fashion.control.dao.product_media_dao import ProductMediaDAO
from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.control.dao.promotion_dao import PromotionDAO
from abc_fashion.control.dao.review_dao import ReviewDAO
from abc_fashion.control.dao.size_chart_entry_dao import SizeChartEntryDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.control.gateway.assistant_engine import AssistantEngine
from abc_fashion.control.gateway.search_engine import SearchEngine
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.assistant import AssistantTurn
from abc_fashion.model.catalogue import FitType, MediaType, StyleStatus, VariantStatus, Category, ProductVariant, Style
from abc_fashion.model.inventory import StockLevel
from abc_fashion.model.sales import promo_price, Promotion
from abc_fashion.model.user import Customer

log = logging.getLogger("abc_fashion")

SIZES = ["XS", "S", "M", "L", "XL", "XXL", "28", "29", "30", "31", "32", "33", "34"]
COLOURS = ["Trắng", "Đen", "Đỏ", "Xanh", "Xám", "Be", "Hồng", "Vàng", "Nâu"]
SORTS = [("Tên A–Z", "name"), ("Giá tăng dần", "price_asc"), ("Giá giảm dần", "price_desc"), ("Mới nhất", "newest")]


class CatalogueController:
    def __init__(self):
        self.category_dao = CategoryDAO()
        self.style_dao = StyleDAO()
        self.product_variant_dao = ProductVariantDAO()
        self.product_media_dao = ProductMediaDAO()
        self.material_component_dao = MaterialComponentDAO()
        self.size_chart_entry_dao = SizeChartEntryDAO()
        self.review_dao = ReviewDAO()
        self.stock_level_dao = StockLevelDAO()
        self.promotion_dao = PromotionDAO()
        self.assistant_turn_dao = AssistantTurnDAO()
        self.search_engine = SearchEngine()
        self.assistant_engine = AssistantEngine()

    # ---------- duyệt / tìm ----------
    def get_categories(self) -> list[Category]:
        return self.category_dao.get_all_category()

    def browse_style(self, category: Category | None, size: str, colour: str, fit_type: FitType | None,
                     min_price: int, max_price: int, sort: str) -> list[Style]:
        """UC04: lọc theo danh mục (gồm danh mục con), cỡ, màu, dáng, khoảng giá; `max_price = 0` là không giới hạn."""
        if min_price < 0 or max_price < 0:
            raise BusinessError("Giá phải là số không âm")
        if max_price and min_price > max_price:
            raise BusinessError("Giá từ phải nhỏ hơn giá đến")
        return self.style_dao.get_style_by_category(category, (size or "").strip(), (colour or "").strip(),
                                                    fit_type.value if fit_type else "", min_price, max_price,
                                                    sort or "name")

    def search_style(self, key: str) -> list[Style]:
        """UC05 tìm bằng chữ; chỉ trả sản phẩm đang bán."""
        key = (key or "").strip()
        if not key:
            raise BusinessError("Nhập từ khoá")
        return [s for s in self.style_dao.search_style(key) if s.status == StyleStatus.ACTIVE]

    def find_style_ids_by_image(self, image: bytes) -> list[int]:
        """UC05 tìm bằng ảnh (CLIP). An toàn ở luồng phụ. Dịch vụ AI không phản hồi → ServiceUnavailable."""
        return self.search_engine.search_by_image(image)

    def find_style_ids_by_voice(self, audio: bytes) -> list[int]:
        """UC05 tìm bằng giọng nói (Whisper + LLM). An toàn ở luồng phụ."""
        return self.search_engine.search_by_voice(audio)

    def get_active_styles(self, ids: list[int]) -> list[Style]:
        """Sản phẩm đang bán theo đúng thứ tự `ids` (kết quả tìm bằng ảnh / giọng nói)."""
        return [s for s in self.style_dao.search_style_by_ids(ids) if s.status == StyleStatus.ACTIVE]

    def get_cover_images(self, styles: list[Style]) -> dict[int, str]:
        """Ảnh đầu tiên (file cục bộ, bỏ URL CDN không tải được) của mỗi style — cho danh sách dạng lưới."""
        out = {}
        for s in styles:
            image = next((m.url for m in self.product_media_dao.get_media_by_style(s)
                          if m.media_type == MediaType.IMAGE and m.url and "://" not in m.url), None)
            if image:
                out[s.id] = image
        return out

    # ---------- trang chi tiết ----------
    def get_style_detail(self, style: Style) -> Style:
        """Style đầy đủ, gắn động: `variants` (đang bán), `media`, `images`, `materials`, `size_chart`, `reviews`
        (đã duyệt), `promotion` (đang chạy) — cũng là ngữ cảnh dữ liệu thật cho AssistantEngine."""
        s = self.style_dao.get_style_detail(style)
        s.variants = [v for v in self.product_variant_dao.get_variant_by_style(s) if v.status == VariantStatus.ACTIVE]
        s.media = self.product_media_dao.get_media_by_style(s)
        s.images = [m for m in s.media if m.media_type == MediaType.IMAGE]
        s.materials = self.material_component_dao.get_material_by_style(s)
        s.size_chart = self.size_chart_entry_dao.get_size_chart_by_style(s)
        s.reviews = self.review_dao.get_approved_review_by_style(s)
        s.promotion = self.promotion_dao.get_active_promotion_by_style(s)
        return s

    @staticmethod
    def auto_promotion(style: Style) -> Promotion | None:
        """Khuyến mãi tự giảm trên trang sản phẩm (chương trình không có mã giảm giá)."""
        p = getattr(style, "promotion", None)
        return p if p is not None and not getattr(p, "voucher_count", 0) else None

    def get_final_price(self, style: Style, variant: ProductVariant) -> int:
        return promo_price(variant.price, self.auto_promotion(style))

    def get_stock_level(self, variant: ProductVariant) -> StockLevel | None:
        return self.stock_level_dao.get_stock_level_by_variant(variant)

    def summarise_reviews(self, style: Style) -> str:
        """UC33: tóm tắt đánh giá; AI lỗi thì trả chuỗi rỗng (trang vẫn hiện bình thường)."""
        try:
            return self.assistant_engine.summarise_reviews(style)
        except Exception:                                   # noqa: BLE001 - lỗi AI → bỏ trống
            log.exception("summarise_reviews")
            return ""

    # ---------- trợ lý AI ----------
    def get_assistant_history(self, customer: Customer | None, style: Style) -> list[AssistantTurn]:
        return self.assistant_turn_dao.get_turn_by_customer(customer, style) if customer is not None else []

    def ask_assistant(self, question: str, style: Style) -> dict:
        """UC32: hỏi trợ lý (style đã gắn ngữ cảnh bởi get_style_detail). An toàn ở luồng phụ."""
        return self.assistant_engine.ask(question, style)

    def save_assistant_turn(self, customer: Customer | None, style: Style, result: dict,
                            latency_ms: int) -> AssistantTurn:
        """Ghi một lượt hỏi đáp (kèm dữ liệu đã dùng để trả lời) sau khi ask_assistant xong."""
        turn = AssistantTurn(question=result["question"], answer=result["answer"], mode=result["mode"],
                             model_name=result["model_name"], latency_ms=latency_ms)
        turn.grounding_events = result["events"]
        self.assistant_turn_dao.add_assistant_turn(turn, customer, style)
        return turn
