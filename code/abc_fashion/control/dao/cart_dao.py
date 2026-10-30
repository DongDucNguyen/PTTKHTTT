"""CartDAO — Giỏ hàng lưu trên server, một giỏ cho mỗi khách (NFR12)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.sales import Cart, CartItem
from abc_fashion.model.user import Customer


class CartDAO(DAO):
    """Bảng tblCart (+tblCartItem). Dùng bởi: CartFrm, StyleDetailFrm; OrderDAO (cùng transaction)."""

    def get_cart_by_customer(self, customer: Customer) -> Cart:
        self.con.execute('INSERT INTO "tblCart"("updated_at","subtotal","customerId") VALUES (now(),0,%s) '
                         'ON CONFLICT ("customerId") DO NOTHING', (customer.id,))
        cart = _to_entity(Cart, self.con.execute('SELECT * FROM "tblCart" WHERE "customerId" = %s',
                                                    (customer.id,)).fetchone())
        rows = self.con.execute(
            'SELECT i."id", i."quantity", i."added_at", i."cartId", i."productVariantId", v."sku", v."size_label", '
            '  v."colour", v."price", v."status", v."styleId", s."name" AS style_name, s."status" AS style_status '
            'FROM "tblCartItem" i JOIN "tblProductVariant" v ON v."id" = i."productVariantId" '
            'JOIN "tblStyle" s ON s."id" = v."styleId" WHERE i."cartId" = %s ORDER BY i."added_at", i."id"',
            (cart.id,)).fetchall()
        cart.items = [_to_entity(CartItem, r) for r in rows]
        subtotal = sum(i.quantity * i.price for i in cart.items)
        if subtotal != cart.subtotal:
            self.con.execute('UPDATE "tblCart" SET "subtotal" = %s WHERE "id" = %s', (subtotal, cart.id))
            cart.subtotal = subtotal
        return cart

    def add_cart_item(self, cart: Cart, item: CartItem) -> bool:
        if (item.quantity or 0) <= 0:
            return False
        with self.con.transaction():
            row = self.con.execute(
                'SELECT l."available", v."status", s."status" AS style_status, '
                '  coalesce((SELECT "quantity" FROM "tblCartItem" WHERE "cartId" = %s AND "productVariantId" = v."id"), 0) AS in_cart '
                'FROM "tblProductVariant" v JOIN "tblStyle" s ON s."id" = v."styleId" '
                'LEFT JOIN "tblStockLevel" l ON l."productVariantId" = v."id" WHERE v."id" = %s',
                (cart.id, item.productVariantId)).fetchone()
            if (row is None or row["status"] != "active" or row["style_status"] != "active"
                    or (row["available"] or 0) < row["in_cart"] + item.quantity):
                return False                         # kiểm tra sơ bộ; kiểm tra thật ở checkout
            r = self.con.execute(
                'INSERT INTO "tblCartItem"("quantity","added_at","cartId","productVariantId") VALUES (%s,now(),%s,%s) '
                'ON CONFLICT ("cartId","productVariantId") DO UPDATE SET "quantity" = "tblCartItem"."quantity" + EXCLUDED."quantity" '
                'RETURNING "id","quantity","added_at"', (item.quantity, cart.id, item.productVariantId)).fetchone()
            self._touch(cart.id)
        item.id, item.quantity, item.added_at, item.cartId = r["id"], r["quantity"], r["added_at"], cart.id
        return True

    def update_cart_item(self, item: CartItem) -> bool:
        if (item.quantity or 0) <= 0:
            return self.delete_cart_item(item)
        with self.con.transaction():
            row = self.con.execute('UPDATE "tblCartItem" SET "quantity" = %s WHERE "id" = %s RETURNING "cartId"',
                                   (item.quantity, item.id)).fetchone()
            if row:
                self._touch(row["cartId"])
        return row is not None

    def delete_cart_item(self, item: CartItem) -> bool:
        with self.con.transaction():
            row = self.con.execute('DELETE FROM "tblCartItem" WHERE "id" = %s RETURNING "cartId"', (item.id,)).fetchone()
            if row:
                self._touch(row["cartId"])
        return row is not None

    def clear_cart(self, cart: Cart) -> bool:
        with self.con.transaction():
            self.con.execute('DELETE FROM "tblCartItem" WHERE "cartId" = %s', (cart.id,))
            self.con.execute('UPDATE "tblCart" SET "subtotal" = 0, "updated_at" = now() WHERE "id" = %s', (cart.id,))
        cart.items, cart.subtotal = [], 0
        return True

    def _touch(self, cart_id: int) -> None:
        self.con.execute(
            'UPDATE "tblCart" SET "updated_at" = now(), "subtotal" = (SELECT coalesce(sum(i."quantity" * v."price"), 0) '
            'FROM "tblCartItem" i JOIN "tblProductVariant" v ON v."id" = i."productVariantId" WHERE i."cartId" = %s) '
            'WHERE "id" = %s', (cart_id, cart_id))
