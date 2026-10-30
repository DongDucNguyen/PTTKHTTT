"""CategoryDAO — Cây danh mục (tự tham chiếu `parentId`)."""
from __future__ import annotations

import psycopg

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.catalogue import category_descendants, Category


class CategoryDAO(DAO):
    """Bảng tblCategory. Dùng bởi: BrowseStyleFrm, EditStyleFrm, ManageStyleFrm, ProfileFrm, SalesReportFrm."""

    def get_all_category(self) -> list[Category]:
        rows = self.con.execute('SELECT * FROM "tblCategory" ORDER BY "parentId" NULLS FIRST, "name"').fetchall()
        return [_to_entity(Category, r) for r in rows]

    def add_category(self, category: Category) -> bool:
        try:
            with self.con.transaction():
                row = self.con.execute('INSERT INTO "tblCategory"("name","parentId") VALUES (%s,%s) RETURNING "id"',
                                       (category.name, category.parentId)).fetchone()
        except psycopg.errors.ForeignKeyViolation:
            return False
        category.id = row["id"]
        return True

    def update_category(self, category: Category) -> bool:
        if category.parentId is not None:
            # chặn vòng lặp: cha mới không được là chính nó hoặc con cháu của nó
            if category.parentId in category_descendants(self.get_all_category(), category.id):
                return False
        try:
            with self.con.transaction():
                n = self.con.execute('UPDATE "tblCategory" SET "name"=%s,"parentId"=%s WHERE "id"=%s',
                                     (category.name, category.parentId, category.id)).rowcount
        except psycopg.errors.ForeignKeyViolation:
            return False
        return n == 1
