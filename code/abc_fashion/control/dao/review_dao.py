"""ReviewDAO — Đánh giá của một dòng đơn đã mua (UNIQUE `orderItemId`)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _Abort, _like, _to_entity, _val
from abc_fashion.model.catalogue import Style
from abc_fashion.model.review import ReviewStatus, Review
from abc_fashion.model.sales import OrderStatus, OrderItem
from abc_fashion.model.user import StaffMember


class ReviewDAO(DAO):
    """Bảng tblReview. Dùng bởi: ManageReviewFrm, OrderDetailFrm, ReviewFrm, StyleDetailFrm."""

    def get_approved_review_by_style(self, style: Style) -> list[Review]:
        rows = self.con.execute(
            'SELECT r.*, v."colour", v."size_label", split_part(c."full_name", \' \', -1) AS reviewer '
            'FROM "tblReview" r JOIN "tblOrderItem" oi ON oi."id" = r."orderItemId" '
            'JOIN "tblOrder" o ON o."id" = oi."orderId" JOIN "tblCustomer" c ON c."id" = o."customerId" '
            'JOIN "tblProductVariant" v ON v."id" = oi."productVariantId" '
            'WHERE v."styleId" = %s AND r."status" = \'approved\' ORDER BY r."created_at" DESC', (style.id,)).fetchall()
        return [_to_entity(Review, r) for r in rows]

    def add_review(self, review: Review, order_item: OrderItem) -> bool:
        if not (1 <= (review.rating or 0) <= 5) or not (review.body or "").strip():
            return False
        try:
            with self.con.transaction():
                st = self.con.execute(
                    'SELECT o."status" FROM "tblOrder" o JOIN "tblOrderItem" i ON i."orderId" = o."id" WHERE i."id" = %s',
                    (order_item.id,)).fetchone()
                if st is None or st["status"] not in (OrderStatus.DELIVERED.value, OrderStatus.COMPLETED.value):
                    raise _Abort()          # chỉ đánh giá hàng đã giao
                row = self.con.execute(
                    'INSERT INTO "tblReview"("rating","body","size_purchased","fit_vote","status","moderation_note",'
                    '"created_at","orderItemId") VALUES (%s,%s,%s,%s,%s,%s,now(),%s) RETURNING "id","created_at"',
                    (review.rating, review.body.strip(), review.size_purchased, _val(review.fit_vote),
                     _val(review.status or ReviewStatus.PENDING), review.moderation_note, order_item.id)).fetchone()
        except (_Abort, *BUSINESS_ERRORS):
            return False
        review.id, review.created_at, review.orderItemId = row["id"], row["created_at"], order_item.id
        return True

    def is_reviewed(self, order_item: OrderItem) -> bool:
        return self.con.execute('SELECT 1 FROM "tblReview" WHERE "orderItemId" = %s',
                                (order_item.id,)).fetchone() is not None

    def search_review(self, key: str, status: str | None, rating: int | None) -> list[Review]:
        status = _val(status) or None
        k = _like(key)
        rows = self.con.execute(
            'SELECT r.*, s."name" AS style_name, v."sku", c."full_name" AS customer_name '
            'FROM "tblReview" r JOIN "tblOrderItem" oi ON oi."id" = r."orderItemId" '
            'JOIN "tblOrder" o ON o."id" = oi."orderId" JOIN "tblCustomer" c ON c."id" = o."customerId" '
            'JOIN "tblProductVariant" v ON v."id" = oi."productVariantId" JOIN "tblStyle" s ON s."id" = v."styleId" '
            'WHERE (r."body" ILIKE %s OR s."name" ILIKE %s) AND (%s::text IS NULL OR r."status" = %s::text) '
            '  AND (%s::int IS NULL OR r."rating" = %s::int) ORDER BY r."created_at" DESC',
            (k, k, status, status, rating, rating)).fetchall()
        return [_to_entity(Review, r) for r in rows]

    def update_review(self, review: Review, staff: StaffMember) -> bool:
        n = self.con.execute(
            'UPDATE "tblReview" SET "status" = %s, "moderation_note" = %s, "staffMemberId" = %s WHERE "id" = %s',
            (_val(review.status), review.moderation_note, staff.id, review.id)).rowcount
        if n == 1:
            review.staffMemberId = staff.id
        return n == 1
