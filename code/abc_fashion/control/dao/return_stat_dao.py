"""ReturnStatDAO — Số liệu trả hàng theo style cho báo cáo (đọc nhiều bảng, không ghi)."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.dao import DAO, _to_entity, _val
from abc_fashion.model.stat import ReturnStat


class ReturnStatDAO(DAO):
    """Dùng bởi: ReturnReportFrm."""

    def get_return_stat(self, start: date, end: date, reason: str | None) -> list[ReturnStat]:
        reason = _val(reason) or None
        rows = self.con.execute(
            'WITH sold AS ('
            '  SELECT v."styleId", SUM(i."quantity") AS q FROM "tblOrderItem" i '
            '  JOIN "tblOrder" o ON o."id" = i."orderId" JOIN "tblProductVariant" v ON v."id" = i."productVariantId" '
            '  WHERE o."status" <> \'cancelled\' AND o."placed_at"::date BETWEEN %s AND %s GROUP BY v."styleId"), '
            'ret AS ('
            '  SELECT v."styleId", SUM(ri."quantity") AS q, mode() WITHIN GROUP (ORDER BY r."reason_code") AS main_reason '
            '  FROM "tblReturnItem" ri JOIN "tblReturnRequest" r ON r."id" = ri."returnRequestId" '
            '  JOIN "tblOrderItem" oi ON oi."id" = ri."orderItemId" '
            '  JOIN "tblProductVariant" v ON v."id" = oi."productVariantId" '
            '  WHERE r."status" <> \'rejected\' AND r."requested_at"::date BETWEEN %s AND %s '
            '    AND (%s::text IS NULL OR r."reason_code" = %s::text) GROUP BY v."styleId") '
            'SELECT s.*, coalesce(sold.q, 0) AS quantity_sold, coalesce(ret.q, 0) AS quantity_returned, '
            '  ret.main_reason, CASE WHEN coalesce(sold.q, 0) > 0 THEN coalesce(ret.q, 0)::real / sold.q END AS return_rate '
            'FROM "tblStyle" s LEFT JOIN sold ON sold."styleId" = s."id" LEFT JOIN ret ON ret."styleId" = s."id" '
            'WHERE ret.q IS NOT NULL OR (%s::text IS NULL AND sold.q IS NOT NULL) '
            'ORDER BY return_rate DESC NULLS LAST, quantity_returned DESC, s."name"',
            (start, end, start, end, reason, reason, reason)).fetchall()
        return [_to_entity(ReturnStat, r) for r in rows]
