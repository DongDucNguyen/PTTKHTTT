"""StyleDAO — Mẫu sản phẩm (thiết kế), cha của các biến thể."""
from __future__ import annotations

import psycopg

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _like, _to_entity, _val
from abc_fashion.model.catalogue import StyleStatus, VariantStatus, Category, Style

_SORT = {
    "price_asc": 'min_price ASC, s."name"',
    "price_desc": 'min_price DESC, s."name"',
    "newest": 's."id" DESC',
    "name": 's."name"',
}

_COLUMNS = ("code", "name", "description", "brand", "fit_type", "care_instructions", "features",
            "model_info", "status", "categoryId", "supplierId", "collectionId")


class StyleDAO(DAO):
    """Bảng tblStyle. Dùng bởi: BrowseStyleFrm, EditStyleFrm, ManageStyleFrm, SearchStyleFrm,
    SelectStyleFrm, StyleDetailFrm."""

    def search_style(self, key: str) -> list[Style]:
        """Mọi trạng thái; màn hình khách tự lọc `active`. Gắn `min_price`, `category_name`."""
        k = _like(key)
        rows = self.con.execute(
            'SELECT s.*, c."name" AS category_name, '
            '  (SELECT min(v."price") FROM "tblProductVariant" v WHERE v."styleId" = s."id" '
            '   AND v."status" = \'active\') AS min_price '
            'FROM "tblStyle" s JOIN "tblCategory" c ON c."id" = s."categoryId" '
            'WHERE s."code" ILIKE %s OR s."name" ILIKE %s OR s."brand" ILIKE %s OR s."description" ILIKE %s '
            'ORDER BY s."name"', (k, k, k, k)).fetchall()
        return [_to_entity(Style, r) for r in rows]

    def search_style_by_ids(self, ids: list[int]) -> list[Style]:
        if not ids:
            return []
        rows = self.con.execute(
            'SELECT s.*, (SELECT min(v."price") FROM "tblProductVariant" v WHERE v."styleId" = s."id" '
            '   AND v."status" = \'active\') AS min_price '
            'FROM "tblStyle" s WHERE s."id" = ANY(%s) AND s."status" = \'active\'', (list(ids),)).fetchall()
        by_id = {r["id"]: _to_entity(Style, r) for r in rows}
        return [by_id[i] for i in ids if i in by_id]          # giữ thứ tự xếp hạng

    def get_style_by_category(self, category: Category, size: str, colour: str, fit_type: str,
                              min_price: int, max_price: int, sort: str) -> list[Style]:
        cat_id = category.id if category else None
        order = _SORT.get(sort, _SORT["name"])
        rows = self.con.execute(
            'WITH RECURSIVE cat AS ('
            '  SELECT "id" FROM "tblCategory" WHERE (%s::int IS NULL AND "parentId" IS NULL) OR "id" = %s::int '
            '  UNION ALL SELECT c."id" FROM "tblCategory" c JOIN cat ON c."parentId" = cat."id") '
            'SELECT s.*, min(v."price") AS min_price FROM "tblStyle" s '
            'JOIN "tblProductVariant" v ON v."styleId" = s."id" '
            'WHERE s."status" = \'active\' AND v."status" = \'active\' '
            '  AND s."categoryId" IN (SELECT "id" FROM cat) '
            '  AND (%s::text = \'\' OR v."size_label" = %s::text) '
            '  AND (%s::text = \'\' OR v."colour" = %s::text) '
            '  AND (%s::text = \'\' OR s."fit_type" = %s::text) '
            '  AND (%s::int = 0 OR v."price" >= %s::int) '
            '  AND (%s::int = 0 OR v."price" <= %s::int) '
            f'GROUP BY s."id" ORDER BY {order}',
            (cat_id, cat_id, size or "", size or "", colour or "", colour or "",
             _val(fit_type) or "", _val(fit_type) or "", min_price or 0, min_price or 0,
             max_price or 0, max_price or 0)).fetchall()
        return [_to_entity(Style, r) for r in rows]

    def get_style_detail(self, style: Style) -> Style:
        row = self.con.execute(
            'SELECT s.*, c."name" AS category_name, p."name" AS supplier_name, k."name" AS collection_name '
            'FROM "tblStyle" s JOIN "tblCategory" c ON c."id" = s."categoryId" '
            'JOIN "tblSupplier" p ON p."id" = s."supplierId" '
            'LEFT JOIN "tblCollection" k ON k."id" = s."collectionId" WHERE s."id" = %s', (style.id,)).fetchone()
        return _to_entity(Style, row) if row else style

    def add_style(self, style: Style) -> bool:
        style.status = style.status or StyleStatus.DRAFT
        if style.status == StyleStatus.ACTIVE:
            return False                    # style mới chưa có vật liệu / biến thể
        try:
            with self.con.transaction():
                row = self.con.execute(
                    f'INSERT INTO "tblStyle"({",".join(chr(34) + c + chr(34) for c in _COLUMNS)}) '
                    f'VALUES ({",".join(["%s"] * len(_COLUMNS))}) RETURNING "id"',
                    tuple(_val(getattr(style, c)) for c in _COLUMNS)).fetchone()
        except BUSINESS_ERRORS:
            return False
        style.id = row["id"]
        return True

    def update_style(self, style: Style) -> bool:
        try:
            with self.con.transaction():
                if style.status == StyleStatus.ACTIVE and not self._is_complete(style):
                    return False
                n = self.con.execute(
                    f'UPDATE "tblStyle" SET {",".join(chr(34) + c + chr(34) + "=%s" for c in _COLUMNS)} WHERE "id"=%s',
                    tuple(_val(getattr(style, c)) for c in _COLUMNS) + (style.id,)).rowcount
        except BUSINESS_ERRORS:
            return False
        return n == 1

    def deactivate_style(self, style: Style) -> bool:
        with self.con.transaction():
            n = self.con.execute('UPDATE "tblStyle" SET "status" = %s WHERE "id" = %s',
                                 (StyleStatus.INACTIVE.value, style.id)).rowcount
            self.con.execute('UPDATE "tblProductVariant" SET "status" = %s WHERE "styleId" = %s',
                             (VariantStatus.DISCONTINUED.value, style.id))
        if n == 1:
            style.status = StyleStatus.INACTIVE
        return n == 1

    def _get_catalogue_for_index(self) -> list[Style]:
        """Style đang bán kèm `category_name`, `colours`, `image_url` — để đẩy chỉ mục tìm kiếm lên dịch vụ AI."""
        rows = self.con.execute(
            'SELECT s.*, c."name" AS category_name, '
            '  coalesce((SELECT array_agg(DISTINCT v."colour") FROM "tblProductVariant" v WHERE v."styleId" = s."id"), \'{}\') AS colours, '
            '  (SELECT m."url" FROM "tblProductMedia" m WHERE m."styleId" = s."id" AND m."media_type" = \'image\' '
            '   ORDER BY m."sort_order", m."id" LIMIT 1) AS image_url '
            'FROM "tblStyle" s JOIN "tblCategory" c ON c."id" = s."categoryId" WHERE s."status" = \'active\' ORDER BY s."id"').fetchall()
        return [_to_entity(Style, r) for r in rows]

    def _is_complete(self, style: Style) -> bool:
        """Đủ điều kiện `active`: vật liệu tổng 100% và ít nhất một biến thể active."""
        row = self.con.execute(
            'SELECT (SELECT coalesce(sum("percent"),0) FROM "tblMaterialComponent" WHERE "styleId" = %s) AS pct, '
            '       (SELECT count(*) FROM "tblProductVariant" WHERE "styleId" = %s AND "status" = \'active\') AS nv',
            (style.id, style.id)).fetchone()
        return row["pct"] == 100 and row["nv"] > 0
