"""SupplierDAO — Nhà cung cấp (cũng đăng nhập được)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.user import Supplier, User


class SupplierDAO(DAO):
    """Bảng tblSupplier. Dùng bởi: EditRestockRequestFrm, EditStyleFrm, ManageRestockFrm, LoginFrm."""

    def get_supplier_by_user(self, user: User) -> Supplier | None:
        row = self.con.execute('SELECT * FROM "tblSupplier" WHERE "userId" = %s', (user.id,)).fetchone()
        return _to_entity(Supplier, row) if row else None

    def get_all_supplier(self) -> list[Supplier]:
        rows = self.con.execute('SELECT * FROM "tblSupplier" ORDER BY "name"').fetchall()
        return [_to_entity(Supplier, r) for r in rows]
