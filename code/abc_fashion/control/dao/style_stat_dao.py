"""StyleStatDAO — Số liệu bán hàng theo style cho báo cáo (đọc nhiều bảng, không ghi)."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.catalogue import Category, Collection
from abc_fashion.model.stat import StyleStat


class StyleStatDAO(DAO):
    """Dùng bởi: SalesReportFrm."""

    def get_style_stat(self, start: date, end: date, category: Category | None,
                       collection: Collection | None) -> list[StyleStat]:
        cat_id = category.id if category else None
        col_id = collection.id if collection else None
        rows = self.con.execute(
            'WITH RECURSIVE cat AS ('
            '  SELECT "id" FROM "tblCategory" WHERE "id" = %s::int '
            '  UNION ALL SELECT c."id" FROM "tblCategory" c JOIN cat ON c."parentId" = cat."id") '
            'SELECT s.*, SUM(i."quantity") AS quantity_sold, SUM(i."line_total") AS revenue, '
            '  COUNT(DISTINCT o."id") AS order_count '
            'FROM "tblOrderItem" i JOIN "tblOrder" o ON o."id" = i."orderId" '
            'JOIN "tblProductVariant" v ON v."id" = i."productVariantId" JOIN "tblStyle" s ON s."id" = v."styleId" '
            'WHERE o."status" <> \'cancelled\' AND o."placed_at"::date BETWEEN %s AND %s '
            '  AND (%s::int IS NULL OR s."categoryId" IN (SELECT "id" FROM cat)) '
            '  AND (%s::int IS NULL OR s."collectionId" = %s::int) '
            'GROUP BY s."id" ORDER BY revenue DESC, s."name"',
            (cat_id, start, end, cat_id, col_id, col_id)).fetchall()
        return [_to_entity(StyleStat, r) for r in rows]
