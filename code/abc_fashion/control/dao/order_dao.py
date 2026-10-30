"""OrderDAO — Đơn hàng (kèm OrderItem, OrderVoucher, và tạo Shipment)."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.cart_dao import CartDAO
from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _Abort, _like, _next_no, _to_entity, _val
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.model.fulfilment import ShipmentDirection, ShipmentStatus
from abc_fashion.model.inventory import MovementReason
from abc_fashion.model.sales import (ORDER_CANCELLABLE, OrderStatus, can_transition, Order, OrderItem,
                                     Voucher)
from abc_fashion.model.user import Customer

_ITEM_SQL = ('SELECT i.*, v."sku", v."size_label", v."colour", v."styleId", v."price", s."name" AS style_name, '
             '  l."stockLocationId" '
             'FROM "tblOrderItem" i JOIN "tblProductVariant" v ON v."id" = i."productVariantId" '
             'JOIN "tblStyle" s ON s."id" = v."styleId" LEFT JOIN "tblStockLevel" l ON l."productVariantId" = v."id" '
             'WHERE i."orderId" = %s ORDER BY i."id"')


class OrderDAO(DAO):
    """Bảng tblOrder. Dùng bởi: CancelRequestFrm, CheckoutFrm, ConfirmOrderFrm, ManageOrderFrm, OrderDetailFrm,
    OrderListFrm, SearchOrderFrm."""

    def add_order(self, order: Order, customer: Customer) -> bool:
        items: list[OrderItem] = getattr(order, "items", [])
        if not items:
            return False
        try:
            with self.con.transaction():
                no = _next_no(self.con, "ORD", "tblOrder", "order_no")                # (1) đầu đơn
                row = self.con.execute(
                    'INSERT INTO "tblOrder"("order_no","status","placed_at","subtotal","discount","shipping_fee",'
                    '"grand_total","delivery_service","note","ship_recipient","ship_phone","ship_address","customerId") '
                    'VALUES (%s,%s,now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING "id","placed_at"',
                    (no, OrderStatus.PENDING_PAYMENT.value, order.subtotal, order.discount, order.shipping_fee,
                     order.grand_total, _val(order.delivery_service), order.note, order.ship_recipient,
                     order.ship_phone, order.ship_address, customer.id)).fetchone()
                order.id, order.order_no, order.placed_at = row["id"], no, row["placed_at"]
                order.status, order.customerId = OrderStatus.PENDING_PAYMENT, customer.id

                for it in items:                                                      # (2) dòng đơn
                    it.id = self.con.execute(
                        'INSERT INTO "tblOrderItem"("quantity","unit_price","discount","line_total","orderId",'
                        '"productVariantId") VALUES (%s,%s,%s,%s,%s,%s) RETURNING "id"',
                        (it.quantity, it.unit_price, it.discount or 0, it.line_total, order.id,
                         it.productVariantId)).fetchone()["id"]
                    it.orderId = order.id

                for v in getattr(order, "vouchers", []):                              # (3) voucher, khoá dòng
                    n = self.con.execute(
                        'UPDATE "tblVoucher" SET "used_count" = "used_count" + 1 '
                        'WHERE "id" = %s AND "used_count" < "usage_limit"', (v.id,)).rowcount
                    if n != 1:
                        raise _Abort("voucher_used_up")
                    self.con.execute('INSERT INTO "tblOrderVoucher"("orderId","voucherId") VALUES (%s,%s)',
                                     (order.id, v.id))

                if not StockLevelDAO().reserve_stock(order):                          # (4) giữ hàng
                    raise _Abort("out_of_stock")

                by_location: dict[int, list[OrderItem]] = {}                       # (5) tách kiện theo kho
                for it in items:
                    loc = self.con.execute('SELECT "stockLocationId" FROM "tblStockLevel" WHERE "productVariantId" = %s',
                                           (it.productVariantId,)).fetchone()
                    by_location.setdefault(loc["stockLocationId"], []).append(it)
                first = True
                for loc_id, group in by_location.items():
                    sid = self.con.execute(
                        'INSERT INTO "tblShipment"("direction","service_level","fee","status","orderId","stockLocationId") '
                        'VALUES (%s,%s,%s,%s,%s,%s) RETURNING "id"',
                        (ShipmentDirection.OUTBOUND.value, _val(order.delivery_service),
                         order.shipping_fee if first else 0, ShipmentStatus.REQUESTED.value, order.id,
                         loc_id)).fetchone()["id"]
                    first = False
                    for it in group:
                        self.con.execute('INSERT INTO "tblShipmentRecord"("quantity","shipmentId","orderItemId") '
                                         'VALUES (%s,%s,%s)', (it.quantity, sid, it.id))

                cart_dao = CartDAO()                                                  # (6) xoá giỏ
                cart_dao.clear_cart(cart_dao.get_cart_by_customer(customer))
            return True
        except (_Abort, *BUSINESS_ERRORS):
            order.id = order.order_no = None
            order.status = None
            return False

    def get_order_by_customer(self, customer: Customer, status: str | None) -> list[Order]:
        status = _val(status) or None
        rows = self.con.execute(
            'SELECT o.*, (SELECT count(*) FROM "tblOrderItem" i WHERE i."orderId" = o."id") AS item_count '
            'FROM "tblOrder" o WHERE o."customerId" = %s AND (%s::text IS NULL OR o."status" = %s::text) '
            'ORDER BY o."placed_at" DESC', (customer.id, status, status)).fetchall()
        return [_to_entity(Order, r) for r in rows]

    def get_order_detail(self, order: Order) -> Order:
        row = self.con.execute(
            'SELECT o.*, c."full_name" AS customer_name, c."phone" AS customer_phone, u."email" AS customer_email, '
            '  c."userId" AS customer_user_id '
            'FROM "tblOrder" o JOIN "tblCustomer" c ON c."id" = o."customerId" JOIN "tblUser" u ON u."id" = c."userId" '
            'WHERE o."id" = %s', (order.id,)).fetchone()
        if row is None:
            return order
        out = _to_entity(Order, row)
        out.items = [_to_entity(OrderItem, r) for r in self.con.execute(_ITEM_SQL, (order.id,)).fetchall()]
        out.vouchers = [_to_entity(Voucher, r) for r in self.con.execute(
            'SELECT v.* FROM "tblVoucher" v JOIN "tblOrderVoucher" ov ON ov."voucherId" = v."id" WHERE ov."orderId" = %s',
            (order.id,)).fetchall()]
        out.payments = PaymentDAO().get_payment_by_order(out)
        out.shipments = ShipmentDAO().get_shipment_by_order(out)
        return out

    def update_order_status(self, order: Order) -> bool:
        new = order.status
        if new == OrderStatus.CANCELLED:
            return self.cancel_order(order)
        head = None
        try:
            with self.con.transaction():
                head = self.con.execute('SELECT "status","order_no" FROM "tblOrder" WHERE "id" = %s FOR UPDATE',
                                        (order.id,)).fetchone()
                if head is None:
                    raise _Abort()
                old = OrderStatus(head["status"])
                if not can_transition(old, new):
                    raise _Abort("invalid_transition")
                n = self.con.execute('UPDATE "tblOrder" SET "status" = %s WHERE "id" = %s AND "status" = %s',
                                     (new.value, order.id, old.value)).rowcount
                if n != 1:
                    raise _Abort()
                if old == OrderStatus.PENDING_PAYMENT and new == OrderStatus.CONFIRMED:
                    self._commit_sale(order.id, head["order_no"])                     # BR2: trừ kho sau thanh toán
                elif new == OrderStatus.DELIVERED:
                    self.con.execute(
                        'UPDATE "tblShipment" SET "status" = %s, "delivered_at" = coalesce("delivered_at", now()) '
                        'WHERE "orderId" = %s AND "direction" = %s AND "returnRequestId" IS NULL AND "status" <> %s',
                        (ShipmentStatus.DELIVERED.value, order.id, ShipmentDirection.OUTBOUND.value,
                         ShipmentStatus.FAILED.value))
        except (_Abort, *BUSINESS_ERRORS):
            order.status = OrderStatus(head["status"]) if head else order.status
            return False
        return True

    def cancel_order(self, order: Order) -> bool:
        if not (order.cancel_reason or "").strip():
            return False
        try:
            with self.con.transaction():
                head = self.con.execute('SELECT "status","order_no" FROM "tblOrder" WHERE "id" = %s FOR UPDATE',
                                        (order.id,)).fetchone()
                if head is None or OrderStatus(head["status"]) not in ORDER_CANCELLABLE:
                    raise _Abort()
                old = OrderStatus(head["status"])
                items = self.con.execute('SELECT "productVariantId", "quantity" FROM "tblOrderItem" WHERE "orderId" = %s '
                                         'ORDER BY "productVariantId"', (order.id,)).fetchall()
                levels = self._lock_levels([r["productVariantId"] for r in items])
                for it in items:
                    level, q = levels[it["productVariantId"]], it["quantity"]
                    if old == OrderStatus.PENDING_PAYMENT:                            # mới giữ hàng → nhả giữ
                        self.con.execute('UPDATE "tblStockLevel" SET "reserved" = "reserved" - %s, '
                                         '"available" = "available" + %s WHERE "id" = %s', (q, q, level["id"]))
                    else:                                                             # đã trừ on_hand → cộng lại
                        self.con.execute('UPDATE "tblStockLevel" SET "on_hand" = "on_hand" + %s, '
                                         '"available" = "available" + %s WHERE "id" = %s', (q, q, level["id"]))
                        self.con.execute(
                            'INSERT INTO "tblStockMovement"("quantity_change","reason","reference","note","created_at",'
                            '"productVariantId","stockLocationId") VALUES (%s,%s,%s,%s,now(),%s,%s)',
                            (q, MovementReason.ADJUSTMENT.value, head["order_no"], "order cancelled",
                             it["productVariantId"], level["stockLocationId"]))
                self.con.execute(
                    'UPDATE "tblVoucher" SET "used_count" = greatest("used_count" - 1, 0) WHERE "id" IN '
                    '(SELECT "voucherId" FROM "tblOrderVoucher" WHERE "orderId" = %s)', (order.id,))
                self.con.execute('UPDATE "tblShipment" SET "status" = %s WHERE "orderId" = %s AND "status" = %s',
                                 (ShipmentStatus.FAILED.value, order.id, ShipmentStatus.REQUESTED.value))
                self.con.execute('UPDATE "tblOrder" SET "status" = %s, "cancel_reason" = %s WHERE "id" = %s AND "status" = %s',
                                 (OrderStatus.CANCELLED.value, order.cancel_reason.strip(), order.id, old.value))
        except (_Abort, *BUSINESS_ERRORS):
            return False
        order.status = OrderStatus.CANCELLED
        return True

    def search_order(self, key: str, status: str | None, start: date, end: date) -> list[Order]:
        status = _val(status) or None
        k = _like(key)
        rows = self.con.execute(
            'SELECT o.*, c."full_name" AS customer_name, u."email" AS customer_email, c."phone" AS customer_phone, '
            '  (o."cancel_reason" IS NOT NULL AND o."status" <> \'cancelled\') AS cancel_requested '
            'FROM "tblOrder" o JOIN "tblCustomer" c ON c."id" = o."customerId" JOIN "tblUser" u ON u."id" = c."userId" '
            'WHERE (o."order_no" ILIKE %s OR c."full_name" ILIKE %s OR u."email" ILIKE %s OR c."phone" ILIKE %s) '
            '  AND (%s::text IS NULL OR o."status" = %s::text) AND o."placed_at"::date BETWEEN %s AND %s '
            'ORDER BY o."placed_at" DESC', (k, k, k, k, status, status, start, end)).fetchall()
        return [_to_entity(Order, r) for r in rows]

    # ---------- riêng tư ----------
    def _get_brief(self, order_id: int) -> Order | None:
        row = self.con.execute('SELECT "id","order_no","status","customerId","grand_total" FROM "tblOrder" WHERE "id" = %s',
                               (order_id,)).fetchone()
        return _to_entity(Order, row) if row else None

    def _status_signature(self, order_id: int) -> tuple:
        """(trạng thái đơn, trạng thái từng kiện) — để màn hình tự nạp lại khi vận chuyển đổi."""
        o = self.con.execute('SELECT "status" FROM "tblOrder" WHERE "id" = %s', (order_id,)).fetchone()
        s = self.con.execute('SELECT "id","status" FROM "tblShipment" WHERE "orderId" = %s ORDER BY "id"', (order_id,)).fetchall()
        return (o["status"] if o else None, tuple((r["id"], r["status"]) for r in s))

    def _request_cancel(self, order: Order) -> bool:
        """Khách gửi yêu cầu huỷ đơn `processing`: lưu `cancel_reason`, giữ trạng thái (mục 9.6, 13 #12)."""
        n = self.con.execute('UPDATE "tblOrder" SET "cancel_reason" = %s WHERE "id" = %s AND "status" = %s',
                             ((order.cancel_reason or "").strip(), order.id, OrderStatus.PROCESSING.value)).rowcount
        return n == 1 and bool((order.cancel_reason or "").strip())

    def _lock_levels(self, variant_ids: list[int]) -> dict[int, dict]:
        rows = self.con.execute('SELECT * FROM "tblStockLevel" WHERE "productVariantId" = ANY(%s) '
                                'ORDER BY "productVariantId" FOR UPDATE', (sorted(set(variant_ids)),)).fetchall()
        return {r["productVariantId"]: r for r in rows}

    def _commit_sale(self, order_id: int, order_no: str) -> None:
        """pending_payment → confirmed: `on_hand −= q`, `reserved −= q` và sổ kho `sale`."""
        items = self.con.execute('SELECT "productVariantId", "quantity" FROM "tblOrderItem" WHERE "orderId" = %s',
                                 (order_id,)).fetchall()
        levels = self._lock_levels([r["productVariantId"] for r in items])
        for it in items:
            level, q = levels[it["productVariantId"]], it["quantity"]
            self.con.execute('UPDATE "tblStockLevel" SET "on_hand" = "on_hand" - %s, "reserved" = "reserved" - %s '
                             'WHERE "id" = %s', (q, q, level["id"]))
            self.con.execute(
                'INSERT INTO "tblStockMovement"("quantity_change","reason","reference","created_at",'
                '"productVariantId","stockLocationId") VALUES (%s,%s,%s,now(),%s,%s)',
                (-q, MovementReason.SALE.value, order_no, it["productVariantId"], level["stockLocationId"]))

    def _cancel_expired_pending(self, minutes: int) -> int:
        """Huỷ đơn `pending_payment` quá hạn để nhả hàng (mục 9.5). Trả số đơn đã huỷ."""
        rows = self.con.execute(
            'SELECT "id" FROM "tblOrder" WHERE "status" = %s AND "placed_at" < now() - make_interval(mins => %s)',
            (OrderStatus.PENDING_PAYMENT.value, minutes)).fetchall()
        done = 0
        for r in rows:
            o = Order(id=r["id"], cancel_reason="Quá hạn thanh toán")
            done += self.cancel_order(o)
        return done
