"""StockLocationDAO — Kho hàng."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.inventory import StockLocation


class StockLocationDAO(DAO):
    """Bảng tblStockLocation. Dùng bởi: EditRestockRequestFrm, EditVariantFrm, StockLevelFrm."""

    def get_all_stock_location(self) -> list[StockLocation]:
        rows = self.con.execute('SELECT * FROM "tblStockLocation" ORDER BY "name"').fetchall()
        return [_to_entity(StockLocation, r) for r in rows]
