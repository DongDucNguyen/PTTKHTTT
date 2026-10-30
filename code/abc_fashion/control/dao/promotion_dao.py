"""PromotionDAO — Chương trình khuyến mãi (kèm PromotionStyle, Voucher)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _Abort, _like, _to_entity, _val
from abc_fashion.model.catalogue import Style
from abc_fashion.model.sales import DiscountType, PromotionStatus, Promotion, Voucher

_COLUMNS = ("name", "promo_type", "discount_type", "discount_value", "min_order_value",
            "starts_at", "ends_at", "status")


def _valid(p: Promotion) -> bool:
    if not (p.name or "").strip() or not p.starts_at or not p.ends_at or p.ends_at <= p.starts_at:
        return False
    if (p.discount_value or 0) <= 0 or (p.min_order_value or 0) < 0:
        return False
    return p.discount_type != DiscountType.PERCENT or 1 <= p.discount_value <= 100


class PromotionDAO(DAO):
    """Bảng tblPromotion. Dùng bởi: EditPromotionFrm, ManagePromotionFrm, StyleDetailFrm, CheckoutFrm."""

    def get_active_promotion_by_style(self, style: Style) -> Promotion | None:
        """Chương trình đang chạy giảm nhiều nhất cho style; gắn `voucher_count` (0 = tự động áp giá)."""
        row = self.con.execute(
            'SELECT p.*, (SELECT count(*) FROM "tblVoucher" v WHERE v."promotionId" = p."id") AS voucher_count '
            'FROM "tblPromotion" p JOIN "tblPromotionStyle" ps ON ps."promotionId" = p."id" '
            'WHERE ps."styleId" = %s AND p."status" = \'active\' AND now() >= p."starts_at" AND now() < p."ends_at" '
            'ORDER BY CASE WHEN p."discount_type" = \'percent\' THEN '
            '  (SELECT coalesce(min("price"),0) FROM "tblProductVariant" WHERE "styleId" = %s) * p."discount_value" / 100 '
            '  ELSE p."discount_value" END DESC, p."id" LIMIT 1', (style.id, style.id)).fetchone()
        return _to_entity(Promotion, row) if row else None

    def search_promotion(self, key: str, status: str | None) -> list[Promotion]:
        status = _val(status) or None
        rows = self.con.execute(
            'SELECT p.*, (SELECT count(*) FROM "tblPromotionStyle" s WHERE s."promotionId" = p."id") AS style_count, '
            '  (SELECT count(*) FROM "tblVoucher" v WHERE v."promotionId" = p."id") AS voucher_count '
            'FROM "tblPromotion" p WHERE p."name" ILIKE %s AND (%s::text IS NULL OR p."status" = %s::text) '
            'ORDER BY p."starts_at" DESC', (_like(key), status, status)).fetchall()
        return [_to_entity(Promotion, r) for r in rows]

    def get_promotion_detail(self, promotion: Promotion) -> Promotion:
        row = self.con.execute('SELECT * FROM "tblPromotion" WHERE "id" = %s', (promotion.id,)).fetchone()
        if row is None:
            return promotion
        out = _to_entity(Promotion, row)
        out.styles = [_to_entity(Style, r) for r in self.con.execute(
            'SELECT s.* FROM "tblStyle" s JOIN "tblPromotionStyle" ps ON ps."styleId" = s."id" '
            'WHERE ps."promotionId" = %s ORDER BY s."name"', (promotion.id,)).fetchall()]
        out.vouchers = [_to_entity(Voucher, r) for r in self.con.execute(
            'SELECT * FROM "tblVoucher" WHERE "promotionId" = %s ORDER BY "code"', (promotion.id,)).fetchall()]
        return out

    def add_promotion(self, promotion: Promotion) -> bool:
        promotion.status = promotion.status or PromotionStatus.DRAFT
        if not _valid(promotion):
            return False
        try:
            with self.con.transaction():
                row = self.con.execute(
                    f'INSERT INTO "tblPromotion"({",".join(chr(34) + c + chr(34) for c in _COLUMNS)}) '
                    f'VALUES ({",".join(["%s"] * len(_COLUMNS))}) RETURNING "id"',
                    tuple(_val(getattr(promotion, c)) for c in _COLUMNS)).fetchone()
                self._save_styles(row["id"], getattr(promotion, "styles", []))
        except BUSINESS_ERRORS:
            return False
        promotion.id = row["id"]
        return True

    def update_promotion(self, promotion: Promotion) -> bool:
        if not _valid(promotion):
            return False
        try:
            with self.con.transaction():
                n = self.con.execute(
                    f'UPDATE "tblPromotion" SET {",".join(chr(34) + c + chr(34) + "=%s" for c in _COLUMNS)} '
                    'WHERE "id" = %s', tuple(_val(getattr(promotion, c)) for c in _COLUMNS) + (promotion.id,)).rowcount
                if n != 1:
                    raise _Abort()
                if hasattr(promotion, "styles"):
                    self.con.execute('DELETE FROM "tblPromotionStyle" WHERE "promotionId" = %s', (promotion.id,))
                    self._save_styles(promotion.id, promotion.styles)
        except (_Abort, *BUSINESS_ERRORS):
            return False
        return True

    def _save_styles(self, promotion_id: int, styles: list[Style]) -> None:
        for sid in dict.fromkeys(s.id for s in styles):
            self.con.execute('INSERT INTO "tblPromotionStyle"("promotionId","styleId") VALUES (%s,%s)',
                             (promotion_id, sid))
