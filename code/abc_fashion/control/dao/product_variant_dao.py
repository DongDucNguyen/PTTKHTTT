"""ProductVariantDAO — SKU: một cỡ + một màu của style, có giá."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _like, _to_entity, _val
from abc_fashion.model.catalogue import VariantStatus, ProductVariant, Style


class ProductVariantDAO(DAO):
    """Bảng tblProductVariant. Dùng bởi: EditStyleFrm, EditVariantFrm, SelectVariantFrm, StyleDetailFrm,
    ReturnRequestFrm."""

    def get_variant_by_style(self, style: Style) -> list[ProductVariant]:
        rows = self.con.execute(
            'SELECT v.*, l."available", l."stockLocationId", k."name" AS location_name '
            'FROM "tblProductVariant" v LEFT JOIN "tblStockLevel" l ON l."productVariantId" = v."id" '
            'LEFT JOIN "tblStockLocation" k ON k."id" = l."stockLocationId" '
            'WHERE v."styleId" = %s ORDER BY v."colour", v."size_label"', (style.id,)).fetchall()
        return [_to_entity(ProductVariant, r) for r in rows]

    def search_variant(self, key: str) -> list[ProductVariant]:
        k = _like(key)
        rows = self.con.execute(
            'SELECT v.*, s."name" AS style_name, l."stockLocationId", k."name" AS location_name '
            'FROM "tblProductVariant" v JOIN "tblStyle" s ON s."id" = v."styleId" '
            'LEFT JOIN "tblStockLevel" l ON l."productVariantId" = v."id" '
            'LEFT JOIN "tblStockLocation" k ON k."id" = l."stockLocationId" '
            'WHERE v."sku" ILIKE %s OR s."name" ILIKE %s ORDER BY s."name", v."colour", v."size_label"',
            (k, k)).fetchall()
        return [_to_entity(ProductVariant, r) for r in rows]

    def add_variant(self, variant: ProductVariant, style: Style) -> bool:
        variant.status = variant.status or VariantStatus.ACTIVE
        try:
            with self.con.transaction():
                row = self.con.execute(
                    'INSERT INTO "tblProductVariant"("sku","size_label","colour","price","status","styleId") '
                    'VALUES (%s,%s,%s,%s,%s,%s) RETURNING "id"',
                    (variant.sku.strip(), variant.size_label.strip(), variant.colour.strip(), variant.price,
                     _val(variant.status), style.id)).fetchone()
        except BUSINESS_ERRORS:
            return False
        variant.id, variant.styleId = row["id"], style.id
        return True

    def update_variant(self, variant: ProductVariant) -> bool:
        try:
            with self.con.transaction():
                n = self.con.execute(
                    'UPDATE "tblProductVariant" SET "sku"=%s,"size_label"=%s,"colour"=%s,"price"=%s,"status"=%s '
                    'WHERE "id"=%s',
                    (variant.sku.strip(), variant.size_label.strip(), variant.colour.strip(), variant.price,
                     _val(variant.status), variant.id)).rowcount
        except BUSINESS_ERRORS:
            return False
        return n == 1
