"""ProductMediaDAO — Ảnh / video của style."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity, _val
from abc_fashion.model.catalogue import ProductMedia, Style


class ProductMediaDAO(DAO):
    """Bảng tblProductMedia. Dùng bởi: EditStyleFrm, StyleDetailFrm.

    Chỉ lưu đường dẫn; sao chép / xoá file trong thư mục media là việc của view.
    """

    def get_media_by_style(self, style: Style) -> list[ProductMedia]:
        rows = self.con.execute('SELECT * FROM "tblProductMedia" WHERE "styleId" = %s ORDER BY "sort_order", "id"',
                                (style.id,)).fetchall()
        return [_to_entity(ProductMedia, r) for r in rows]

    def add_media(self, media: ProductMedia, style: Style) -> bool:
        row = self.con.execute(
            'INSERT INTO "tblProductMedia"("url","media_type","colour","sort_order","styleId") '
            'VALUES (%s,%s,%s,(SELECT coalesce(max("sort_order"),0) + 1 FROM "tblProductMedia" WHERE "styleId" = %s),%s) '
            'RETURNING "id","sort_order"',
            (media.url, _val(media.media_type), media.colour, style.id, style.id)).fetchone()
        media.id, media.sort_order, media.styleId = row["id"], row["sort_order"], style.id
        return True

    def delete_media(self, media: ProductMedia) -> bool:
        return self.con.execute('DELETE FROM "tblProductMedia" WHERE "id" = %s', (media.id,)).rowcount == 1
