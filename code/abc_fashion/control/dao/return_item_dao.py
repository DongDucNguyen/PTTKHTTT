"""ReturnItemDAO — Dòng trả, dùng cho báo cáo chi tiết."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.catalogue import Style
from abc_fashion.model.returns import ReturnItem


class ReturnItemDAO(DAO):
    """Bảng tblReturnItem. Dùng bởi: ReturnDetailFrm."""

    def get_return_item_by_style(self, style: Style, start: date, end: date) -> list[ReturnItem]:
        rows = self.con.execute(
            'SELECT ri.*, r."reason_code", r."return_no", r."requested_at", r."status" AS request_status, '
            '  oi."unit_price", oi."discount", oi."quantity" AS ordered_quantity, v."sku", v."colour", v."size_label", '
            '  v."styleId", o."order_no" '
            'FROM "tblReturnItem" ri JOIN "tblReturnRequest" r ON r."id" = ri."returnRequestId" '
            'JOIN "tblOrder" o ON o."id" = r."orderId" '
            'JOIN "tblOrderItem" oi ON oi."id" = ri."orderItemId" '
            'JOIN "tblProductVariant" v ON v."id" = oi."productVariantId" '
            'WHERE v."styleId" = %s AND r."status" <> \'rejected\' AND r."requested_at"::date BETWEEN %s AND %s '
            'ORDER BY r."requested_at" DESC', (style.id, start, end)).fetchall()
        return [_to_entity(ReturnItem, r) for r in rows]
