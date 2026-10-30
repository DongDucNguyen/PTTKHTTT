"""SizeChartEntryDAO — Bảng số đo theo cỡ."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _to_entity, _val
from abc_fashion.model.catalogue import SizeChartEntry, Style


class SizeChartEntryDAO(DAO):
    """Bảng tblSizeChartEntry. Dùng bởi: EditStyleFrm, StyleDetailFrm."""

    def get_size_chart_by_style(self, style: Style) -> list[SizeChartEntry]:
        rows = self.con.execute('SELECT * FROM "tblSizeChartEntry" WHERE "styleId" = %s ORDER BY "size_label", "measure"',
                                (style.id,)).fetchall()
        return [_to_entity(SizeChartEntry, r) for r in rows]

    def save_size_chart(self, style: Style, entries: list[SizeChartEntry]) -> bool:
        if any(not e.size_label or (e.value_cm or 0) <= 0 for e in entries):
            return False
        try:
            with self.con.transaction():
                self.con.execute('DELETE FROM "tblSizeChartEntry" WHERE "styleId" = %s', (style.id,))
                for e in entries:
                    e.id = self.con.execute(
                        'INSERT INTO "tblSizeChartEntry"("size_label","measure","value_cm","styleId") '
                        'VALUES (%s,%s,%s,%s) RETURNING "id"',
                        (e.size_label.strip(), _val(e.measure), e.value_cm, style.id)).fetchone()["id"]
                    e.styleId = style.id
        except BUSINESS_ERRORS:            # trùng (cỡ, số đo)
            return False
        return True
