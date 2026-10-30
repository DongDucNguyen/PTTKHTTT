"""StockMovementDAO — Sổ kho: mỗi thay đổi tồn là một dòng."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.dao import DAO, _to_entity, _val
from abc_fashion.model.catalogue import ProductVariant
from abc_fashion.model.inventory import StockMovement


class StockMovementDAO(DAO):
    """Bảng tblStockMovement. Dùng bởi: InspectReturnFrm, ManageOrderFrm, ManageRestockFrm, StockMovementFrm."""

    def add_stock_movement(self, movement: StockMovement) -> bool:
        """Ghi sổ mà không đổi tồn (tồn đã được đổi bởi hàm khác trong cùng transaction)."""
        row = self.con.execute(
            'INSERT INTO "tblStockMovement"("quantity_change","reason","reference","note","created_at",'
            '"productVariantId","stockLocationId","staffMemberId") VALUES (%s,%s,%s,%s,now(),%s,%s,%s) '
            'RETURNING "id","created_at"',
            (movement.quantity_change, _val(movement.reason), movement.reference, movement.note,
             movement.productVariantId, movement.stockLocationId, movement.staffMemberId)).fetchone()
        movement.id, movement.created_at = row["id"], row["created_at"]
        return True

    def get_movement_by_variant(self, variant: ProductVariant, start: date, end: date,
                                reason: str | None) -> list[StockMovement]:
        reason = _val(reason) or None
        rows = self.con.execute(
            'SELECT m.*, s."full_name" AS staff_name, k."name" AS location_name FROM "tblStockMovement" m '
            'LEFT JOIN "tblStaffMember" s ON s."id" = m."staffMemberId" '
            'JOIN "tblStockLocation" k ON k."id" = m."stockLocationId" '
            'WHERE m."productVariantId" = %s AND m."created_at" >= %s::date AND m."created_at" < %s::date + 1 '
            '  AND (%s::text IS NULL OR m."reason" = %s::text) ORDER BY m."created_at" DESC, m."id" DESC',
            (variant.id, start, end, reason, reason)).fetchall()
        return [_to_entity(StockMovement, r) for r in rows]
