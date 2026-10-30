"""CollectionDAO — Bộ sưu tập theo mùa."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.catalogue import Collection


class CollectionDAO(DAO):
    """Bảng tblCollection. Dùng bởi: EditStyleFrm, SalesReportFrm."""

    def get_all_collection(self) -> list[Collection]:
        rows = self.con.execute('SELECT * FROM "tblCollection" ORDER BY "year" DESC, "name"').fetchall()
        return [_to_entity(Collection, r) for r in rows]
