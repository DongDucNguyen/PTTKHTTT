"""ReviewController — khách đánh giá sản phẩm đã mua (UC13, kiểm duyệt AI UC34) và nhân viên duyệt đánh giá (UC19)."""
from __future__ import annotations

from abc_fashion.control.dao.review_dao import ReviewDAO
from abc_fashion.control.gateway.assistant_engine import AssistantEngine
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.review import FitVote, ReviewStatus, Review
from abc_fashion.model.sales import OrderItem
from abc_fashion.model.user import StaffMember


class ReviewController:
    def __init__(self):
        self.review_dao = ReviewDAO()
        self.assistant_engine = AssistantEngine()

    def submit_review(self, order_item: OrderItem, rating: int, body: str, size_purchased: str,
                      fit_vote: FitVote) -> Review:
        """Trả đánh giá đã lưu: `status` approved nếu qua kiểm duyệt tự động, pending (kèm `moderation_note`) nếu không."""
        body = (body or "").strip()
        if not (1 <= (rating or 0) <= 5):
            raise BusinessError("Số sao từ 1 đến 5")
        if not body:
            raise BusinessError("Nhập nội dung nhận xét")
        if self.review_dao.is_reviewed(order_item):
            raise BusinessError("Bạn đã đánh giá sản phẩm này")
        review = Review(rating=rating, body=body, size_purchased=(size_purchased or "").strip() or None,
                        fit_vote=fit_vote)
        try:
            ok, note = self.assistant_engine.moderate(review)                            # UC34
        except Exception:                                                                # noqa: BLE001 - AI lỗi → duyệt tay
            ok, note = False, "Kiểm duyệt tự động không khả dụng"
        review.status = ReviewStatus.APPROVED if ok else ReviewStatus.PENDING
        review.moderation_note = note or None
        if not self.review_dao.add_review(review, order_item):
            raise BusinessError("Không gửi được đánh giá (đơn chưa giao hoặc đã đánh giá)")
        return review

    def search_review(self, key: str, status: ReviewStatus | None, rating: int | None) -> list[Review]:
        return self.review_dao.search_review(key or "", status, rating or None)

    def moderate_review(self, staff: StaffMember, review: Review, status: ReviewStatus, note: str) -> bool:
        note = (note or "").strip()
        if status == ReviewStatus.REJECTED and not note:
            raise BusinessError("Nhập lý do từ chối")
        review.status, review.moderation_note = status, note or None
        return self.review_dao.update_review(review, staff)
