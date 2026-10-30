"""MaterialComponentDAO — Thành phần vải của style."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.catalogue import MaterialComponent, Style


class MaterialComponentDAO(DAO):
    """Bảng tblMaterialComponent. Dùng bởi: EditStyleFrm, StyleDetailFrm."""

    def get_material_by_style(self, style: Style) -> list[MaterialComponent]:
        rows = self.con.execute('SELECT * FROM "tblMaterialComponent" WHERE "styleId" = %s ORDER BY "percent" DESC',
                                (style.id,)).fetchall()
        return [_to_entity(MaterialComponent, r) for r in rows]

    def save_material(self, style: Style, materials: list[MaterialComponent]) -> bool:
        if any(not m.material or not (1 <= (m.percent or 0) <= 100) for m in materials):
            return False
        if materials and sum(m.percent for m in materials) != 100:
            return False
        if len({m.material.strip().lower() for m in materials}) != len(materials):
            return False                    # trùng tên vật liệu (CSDL báo cáo có UNIQUE ("styleId", material))
        with self.con.transaction():
            self.con.execute('DELETE FROM "tblMaterialComponent" WHERE "styleId" = %s', (style.id,))
            for m in materials:
                m.id = self.con.execute(
                    'INSERT INTO "tblMaterialComponent"("material","percent","styleId") VALUES (%s,%s,%s) RETURNING "id"',
                    (m.material.strip(), m.percent, style.id)).fetchone()["id"]
                m.styleId = style.id
        return True
