"""VoucherDAO — Mã giảm giá của một chương trình."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _to_entity
from abc_fashion.model.sales import Promotion, Voucher


class VoucherDAO(DAO):
    """Bảng tblVoucher. Dùng bởi: CheckoutFrm, EditPromotionFrm."""

    def get_voucher_by_code(self, code: str) -> Voucher | None:
        """Gắn `voucher.promotion` (kèm `promotion.style_ids`)."""
        row = self.con.execute('SELECT * FROM "tblVoucher" WHERE upper("code") = upper(%s)',
                               ((code or "").strip(),)).fetchone()
        if row is None:
            return None
        voucher = _to_entity(Voucher, row)
        promotion = _to_entity(Promotion, self.con.execute(
            'SELECT * FROM "tblPromotion" WHERE "id" = %s', (voucher.promotionId,)).fetchone())
        promotion.style_ids = {r["styleId"] for r in self.con.execute(
            'SELECT "styleId" FROM "tblPromotionStyle" WHERE "promotionId" = %s', (promotion.id,)).fetchall()}
        voucher.promotion = promotion
        return voucher

    def add_voucher(self, voucher: Voucher, promotion: Promotion) -> bool:
        if not (voucher.code or "").strip() or (voucher.usage_limit or 0) <= 0:
            return False
        try:
            with self.con.transaction():
                row = self.con.execute(
                    'INSERT INTO "tblVoucher"("code","usage_limit","used_count","promotionId") VALUES (%s,%s,0,%s) '
                    'RETURNING "id"', (voucher.code.strip().upper(), voucher.usage_limit, promotion.id)).fetchone()
        except BUSINESS_ERRORS:
            return False
        voucher.id, voucher.used_count, voucher.promotionId = row["id"], 0, promotion.id
        voucher.code = voucher.code.strip().upper()
        return True

    def get_voucher_by_promotion(self, promotion: Promotion) -> list[Voucher]:
        rows = self.con.execute('SELECT * FROM "tblVoucher" WHERE "promotionId" = %s ORDER BY "code"',
                                (promotion.id,)).fetchall()
        return [_to_entity(Voucher, r) for r in rows]
