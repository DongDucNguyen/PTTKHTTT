"""ReturnRequestDAO — Yêu cầu trả / đổi hàng (kèm ReturnItem, ReturnEvidence). Mỗi đơn tối đa một yêu cầu."""
from __future__ import annotations

import psycopg

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _Abort, _like, _next_no, _to_entity, _val
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.model.fulfilment import Shipment
from abc_fashion.model.returns import (RETURN_NEXT, InspectionResult, ReturnStatus, ReturnEvidence, ReturnItem,
                                       ReturnRequest, within_return_window)
from abc_fashion.model.sales import OrderStatus, Order
from abc_fashion.model.user import StaffMember

_ITEM_SQL = (
    'SELECT ri.*, oi."unit_price", oi."discount", oi."orderId", oi."productVariantId", '
    '  oi."quantity" AS ordered_quantity, v."sku", v."size_label", v."colour", v."styleId", v."price", '
    '  s."name" AS style_name, rv."sku" AS replacement_sku, rv."colour" AS replacement_colour, '
    '  rv."size_label" AS replacement_size, l."stockLocationId", l."id" AS stock_level_id '
    'FROM "tblReturnItem" ri JOIN "tblOrderItem" oi ON oi."id" = ri."orderItemId" '
    'JOIN "tblProductVariant" v ON v."id" = oi."productVariantId" JOIN "tblStyle" s ON s."id" = v."styleId" '
    'LEFT JOIN "tblProductVariant" rv ON rv."id" = ri."replacementVariantId" '
    'LEFT JOIN "tblStockLevel" l ON l."productVariantId" = v."id" '
    'WHERE ri."returnRequestId" = %s ORDER BY ri."id"')


class ReturnRequestDAO(DAO):
    """Bảng tblReturnRequest. Dùng bởi: InspectReturnFrm, OrderDetailFrm, ProcessReturnFrm, ReturnRequestFrm,
    SearchReturnRequestFrm."""

    def add_return_request(self, request: ReturnRequest, order: Order) -> bool:
        items: list[ReturnItem] = getattr(request, "items", [])
        evidence: list[ReturnEvidence] = getattr(request, "evidence", [])
        if not items or request.reason_code is None:
            return False
        try:
            with self.con.transaction():
                head = self.con.execute('SELECT "status" FROM "tblOrder" WHERE "id" = %s FOR UPDATE',
                                        (order.id,)).fetchone()
                if head is None or head["status"] not in (OrderStatus.DELIVERED.value, OrderStatus.COMPLETED.value):
                    raise _Abort()
                delivered = self.con.execute(
                    'SELECT max("delivered_at") AS d, localtimestamp AS now FROM "tblShipment" '
                    'WHERE "orderId" = %s AND "direction" = \'outbound\' AND "returnRequestId" IS NULL', (order.id,)).fetchone()
                if not within_return_window(delivered["d"], delivered["now"]):
                    raise _Abort("window")
                bought = {r["id"]: r["quantity"] for r in self.con.execute(
                    'SELECT "id","quantity" FROM "tblOrderItem" WHERE "orderId" = %s', (order.id,)).fetchall()}
                if any(i.orderItemId not in bought or not (0 < i.quantity <= bought[i.orderItemId]) for i in items):
                    raise _Abort("quantity")
                no = _next_no(self.con, "RET", "tblReturnRequest", "return_no")
                row = self.con.execute(
                    'INSERT INTO "tblReturnRequest"("return_no","return_type","reason_code","reason_detail",'
                    '"desired_resolution","status","requested_at","orderId") VALUES (%s,%s,%s,%s,%s,%s,now(),%s) '
                    'RETURNING "id","requested_at"',
                    (no, _val(request.return_type), _val(request.reason_code), request.reason_detail,
                     _val(request.desired_resolution), ReturnStatus.REQUESTED.value, order.id)).fetchone()
                for i in items:
                    i.id = self.con.execute(
                        'INSERT INTO "tblReturnItem"("quantity","inspection_result","returnRequestId","orderItemId",'
                        '"replacementVariantId") VALUES (%s,%s,%s,%s,%s) RETURNING "id"',
                        (i.quantity, InspectionResult.PENDING.value, row["id"], i.orderItemId,
                         i.replacementVariantId)).fetchone()["id"]
                    i.returnRequestId, i.inspection_result = row["id"], InspectionResult.PENDING
                for e in evidence:
                    e.id = self.con.execute(
                        'INSERT INTO "tblReturnEvidence"("url","media_type","returnRequestId") VALUES (%s,%s,%s) '
                        'RETURNING "id"', (e.url, _val(e.media_type), row["id"])).fetchone()["id"]
                    e.returnRequestId = row["id"]
        except (_Abort, *BUSINESS_ERRORS):           # UNIQUE orderId: đơn đã có yêu cầu trả
            return False
        request.id, request.return_no, request.requested_at = row["id"], no, row["requested_at"]
        request.status, request.orderId = ReturnStatus.REQUESTED, order.id
        return True

    def get_return_request_by_order(self, order: Order) -> ReturnRequest | None:
        row = self.con.execute('SELECT * FROM "tblReturnRequest" WHERE "orderId" = %s', (order.id,)).fetchone()
        return _to_entity(ReturnRequest, row) if row else None

    def search_return_request(self, key: str, status: str | None) -> list[ReturnRequest]:
        status = _val(status) or None
        k = _like(key)
        rows = self.con.execute(
            'SELECT r.*, o."order_no", c."full_name" AS customer_name FROM "tblReturnRequest" r '
            'JOIN "tblOrder" o ON o."id" = r."orderId" JOIN "tblCustomer" c ON c."id" = o."customerId" '
            'WHERE (r."return_no" ILIKE %s OR o."order_no" ILIKE %s OR c."full_name" ILIKE %s) '
            '  AND (%s::text IS NULL OR r."status" = %s::text) ORDER BY r."requested_at" DESC',
            (k, k, k, status, status)).fetchall()
        return [_to_entity(ReturnRequest, r) for r in rows]

    def get_return_request_detail(self, request: ReturnRequest) -> ReturnRequest:
        row = self.con.execute(
            'SELECT r.*, o."order_no", o."customerId", o."ship_address", c."full_name" AS customer_name, '
            '  u."email" AS customer_email, '
            '  (SELECT max(sh."delivered_at") FROM "tblShipment" sh WHERE sh."orderId" = o."id" '
            '     AND sh."direction" = \'outbound\' AND sh."returnRequestId" IS NULL) AS delivered_at '
            'FROM "tblReturnRequest" r JOIN "tblOrder" o ON o."id" = r."orderId" '
            'JOIN "tblCustomer" c ON c."id" = o."customerId" JOIN "tblUser" u ON u."id" = c."userId" '
            'WHERE r."id" = %s', (request.id,)).fetchone()
        if row is None:
            return request
        out = _to_entity(ReturnRequest, row)
        out.items = [_to_entity(ReturnItem, r) for r in self.con.execute(_ITEM_SQL, (request.id,)).fetchall()]
        out.evidence = [_to_entity(ReturnEvidence, r) for r in self.con.execute(
            'SELECT * FROM "tblReturnEvidence" WHERE "returnRequestId" = %s ORDER BY "id"', (request.id,)).fetchall()]
        shipments = [_to_entity(Shipment, r) for r in self.con.execute(
            'SELECT sh.*, k."name" AS location_name FROM "tblShipment" sh '
            'JOIN "tblStockLocation" k ON k."id" = sh."stockLocationId" WHERE sh."returnRequestId" = %s ORDER BY sh."id"',
            (request.id,)).fetchall()]
        ShipmentDAO()._attach_records(shipments)
        out.shipments = shipments
        return out

    def update_return_request(self, request: ReturnRequest, staff: StaffMember) -> bool:
        try:
            with self.con.transaction():
                old = self.con.execute('SELECT "status" FROM "tblReturnRequest" WHERE "id" = %s FOR UPDATE',
                                       (request.id,)).fetchone()
                if old is None or request.status not in RETURN_NEXT[ReturnStatus(old["status"])]:
                    raise _Abort()
                decided = request.status in (ReturnStatus.AUTHORISED, ReturnStatus.REJECTED)
                row = self.con.execute(
                    'UPDATE "tblReturnRequest" SET "status" = %s, "decision_note" = coalesce(%s, "decision_note"), '
                    '"decided_at" = CASE WHEN %s THEN now() ELSE "decided_at" END, "staffMemberId" = %s '
                    'WHERE "id" = %s AND "status" = %s RETURNING "decided_at"',
                    (request.status.value, request.decision_note, decided, staff.id, request.id,
                     old["status"])).fetchone()
                if row is None:
                    raise _Abort()
        except (_Abort, psycopg.errors.CheckViolation):
            return False
        request.decided_at, request.staffMemberId = row["decided_at"], staff.id
        return True

    def update_return_item(self, item: ReturnItem) -> bool:
        n = self.con.execute('UPDATE "tblReturnItem" SET "inspection_result" = %s, "inspection_note" = %s WHERE "id" = %s',
                             (_val(item.inspection_result), item.inspection_note, item.id)).rowcount
        return n == 1
