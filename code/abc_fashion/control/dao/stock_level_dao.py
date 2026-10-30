"""StockLevelDAO — Tồn kho: mỗi biến thể đúng một dòng ở một kho."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _like, _to_entity, _val
from abc_fashion.model.catalogue import ProductVariant
from abc_fashion.model.inventory import StockLevel, StockLocation, StockMovement
from abc_fashion.model.sales import CartItem, Order


class StockLevelDAO(DAO):
    """Bảng tblStockLevel (+tblStockMovement). `available = on_hand − reserved`, `reserved ≤ on_hand`.

    Dùng bởi: AdjustStockFrm, CartFrm, EditVariantFrm, InspectReturnFrm, ManageRestockFrm, StockLevelFrm,
    StyleDetailFrm, ProcessReturnFrm; OrderDAO (cùng transaction).
    """

    def get_stock_level_by_variant(self, variant: ProductVariant) -> StockLevel | None:
        row = self.con.execute(
            'SELECT l.*, v."sku", k."name" AS location_name FROM "tblStockLevel" l '
            'JOIN "tblProductVariant" v ON v."id" = l."productVariantId" '
            'JOIN "tblStockLocation" k ON k."id" = l."stockLocationId" WHERE l."productVariantId" = %s',
            (variant.id,)).fetchone()
        return _to_entity(StockLevel, row) if row else None

    def check_availability(self, items: list[CartItem]) -> list[CartItem]:
        need: dict[int, int] = {}
        for it in items:
            need[it.productVariantId] = need.get(it.productVariantId, 0) + it.quantity
        if not need:
            return []
        rows = self.con.execute(
            'SELECT l."productVariantId", l."available", v."status" AS v_status, s."status" AS s_status '
            'FROM "tblStockLevel" l JOIN "tblProductVariant" v ON v."id" = l."productVariantId" '
            'JOIN "tblStyle" s ON s."id" = v."styleId" WHERE l."productVariantId" = ANY(%s)',
            (list(need),)).fetchall()
        ok = {r["productVariantId"]: r for r in rows}
        bad = []
        for it in items:
            r = ok.get(it.productVariantId)
            it.available = r["available"] if r else 0
            if (r is None or r["v_status"] != "active" or r["s_status"] != "active"
                    or r["available"] < need[it.productVariantId]):
                bad.append(it)
        return bad

    def reserve_stock(self, order: Order) -> bool:
        need: dict[int, int] = {}
        for it in order.items:
            need[it.productVariantId] = need.get(it.productVariantId, 0) + it.quantity
        with self.con.transaction():                           # savepoint nếu đang trong add_order
            rows = self.con.execute(
                'SELECT "id","productVariantId","available" FROM "tblStockLevel" '
                'WHERE "productVariantId" = ANY(%s) ORDER BY "productVariantId" FOR UPDATE',
                (list(need),)).fetchall()
            if len(rows) != len(need) or any(r["available"] < need[r["productVariantId"]] for r in rows):
                return False
            for r in rows:
                q = need[r["productVariantId"]]
                self.con.execute('UPDATE "tblStockLevel" SET "reserved" = "reserved" + %s, '
                                 '"available" = "available" - %s WHERE "id" = %s', (q, q, r["id"]))
        return True

    def add_stock_level(self, level: StockLevel, variant: ProductVariant, location: StockLocation) -> bool:
        try:
            with self.con.transaction():
                row = self.con.execute(
                    'INSERT INTO "tblStockLevel"("on_hand","reserved","reorder_point","available",'
                    '"productVariantId","stockLocationId") VALUES (0,0,%s,0,%s,%s) RETURNING "id"',
                    (level.reorder_point or 0, variant.id, location.id)).fetchone()
        except BUSINESS_ERRORS:
            return False
        level.id, level.on_hand, level.reserved, level.available = row["id"], 0, 0, 0
        level.productVariantId, level.stockLocationId = variant.id, location.id
        return True

    def search_stock_level(self, location: StockLocation | None, key: str,
                           below_reorder_point: bool) -> list[StockLevel]:
        loc_id = location.id if location else None
        k = _like(key)
        rows = self.con.execute(
            'SELECT l.*, v."sku", v."colour", v."size_label", s."name" AS style_name, k."name" AS location_name '
            'FROM "tblStockLevel" l JOIN "tblProductVariant" v ON v."id" = l."productVariantId" '
            'JOIN "tblStyle" s ON s."id" = v."styleId" JOIN "tblStockLocation" k ON k."id" = l."stockLocationId" '
            'WHERE (%s::int IS NULL OR l."stockLocationId" = %s::int) '
            '  AND (v."sku" ILIKE %s OR s."name" ILIKE %s) '
            '  AND (NOT %s::boolean OR l."available" <= l."reorder_point") '
            'ORDER BY s."name", v."colour", v."size_label"',
            (loc_id, loc_id, k, k, bool(below_reorder_point))).fetchall()
        return [_to_entity(StockLevel, r) for r in rows]

    def adjust_stock(self, level: StockLevel, movement: StockMovement) -> bool:
        change = movement.quantity_change or 0
        if change == 0 or movement.reason is None:
            return False
        with self.con.transaction():
            row = self.con.execute('SELECT * FROM "tblStockLevel" WHERE "id" = %s FOR UPDATE', (level.id,)).fetchone()
            if row is None or row["on_hand"] + change < row["reserved"]:
                return False                                   # không âm, không dưới số đang giữ
            new = self.con.execute(
                'UPDATE "tblStockLevel" SET "on_hand" = "on_hand" + %s, "available" = "available" + %s '
                'WHERE "id" = %s RETURNING "on_hand","reserved","available"', (change, change, level.id)).fetchone()
            m = self.con.execute(
                'INSERT INTO "tblStockMovement"("quantity_change","reason","reference","note","created_at",'
                '"productVariantId","stockLocationId","staffMemberId") VALUES (%s,%s,%s,%s,now(),%s,%s,%s) '
                'RETURNING "id","created_at"',
                (change, _val(movement.reason), movement.reference, movement.note, row["productVariantId"],
                 row["stockLocationId"], movement.staffMemberId)).fetchone()
        level.on_hand, level.reserved, level.available = new["on_hand"], new["reserved"], new["available"]
        movement.id, movement.created_at = m["id"], m["created_at"]
        movement.productVariantId, movement.stockLocationId = row["productVariantId"], row["stockLocationId"]
        return True
