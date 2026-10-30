"""OrderItemDAO — Dòng đơn, dùng cho báo cáo chi tiết."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.catalogue import Style
from abc_fashion.model.sales import OrderItem


class OrderItemDAO(DAO):
    """Bảng tblOrderItem. Dùng bởi: SalesDetailFrm."""

    def get_order_item_by_style(self, style: Style, start: date, end: date) -> list[OrderItem]:
        rows = self.con.execute(
            'SELECT i.*, o."order_no", o."placed_at", v."sku", v."colour", v."size_label", v."styleId" '
            'FROM "tblOrderItem" i JOIN "tblOrder" o ON o."id" = i."orderId" '
            'JOIN "tblProductVariant" v ON v."id" = i."productVariantId" '
            'WHERE v."styleId" = %s AND o."status" <> \'cancelled\' AND o."placed_at"::date BETWEEN %s AND %s '
            'ORDER BY o."placed_at" DESC, i."id"', (style.id, start, end)).fetchall()
        return [_to_entity(OrderItem, r) for r in rows]
