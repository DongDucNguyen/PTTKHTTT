"""SavedSizeDAO — Cỡ đã lưu của khách theo danh mục."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.customer_data import SavedSize
from abc_fashion.model.user import Customer


class SavedSizeDAO(DAO):
    """Bảng tblSavedSize. Dùng bởi: ProfileFrm."""

    def get_saved_size_by_customer(self, customer: Customer) -> list[SavedSize]:
        rows = self.con.execute(
            'SELECT z.*, c."name" AS category_name FROM "tblSavedSize" z '
            'JOIN "tblCategory" c ON c."id" = z."categoryId" WHERE z."customerId" = %s ORDER BY c."name"',
            (customer.id,)).fetchall()
        return [_to_entity(SavedSize, r) for r in rows]

    def save_saved_size(self, size: SavedSize, customer: Customer) -> bool:
        row = self.con.execute(
            'INSERT INTO "tblSavedSize"("size_label","customerId","categoryId") VALUES (%s,%s,%s) '
            'ON CONFLICT ("customerId","categoryId") DO UPDATE SET "size_label" = EXCLUDED."size_label" '
            'RETURNING "id"', (size.size_label, customer.id, size.categoryId)).fetchone()
        size.id, size.customerId = row["id"], customer.id
        return True
