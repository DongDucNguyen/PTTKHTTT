"""RestockRequestDAO — Phiếu yêu cầu nhập hàng gửi nhà cung cấp (kèm RestockItem)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _Abort, _next_no, _to_entity, _val
from abc_fashion.model.inventory import RESTOCK_NEXT, MovementReason, RestockStatus, RestockItem, RestockRequest
from abc_fashion.model.user import StaffMember, Supplier


class RestockRequestDAO(DAO):
    """Bảng tblRestockRequest. Dùng bởi: ConfirmRestockFrm, EditRestockRequestFrm, ManageRestockFrm, SupplierHomeFrm."""

    def search_restock_request(self, status: str | None, supplier: Supplier | None) -> list[RestockRequest]:
        status = _val(status) or None
        sup_id = supplier.id if supplier else None
        rows = self.con.execute(
            'SELECT r.*, p."name" AS supplier_name, k."name" AS location_name, '
            '  (SELECT count(*) FROM "tblRestockItem" i WHERE i."restockRequestId" = r."id") AS item_count, '
            '  (SELECT coalesce(sum(i."quantity"),0) FROM "tblRestockItem" i WHERE i."restockRequestId" = r."id") AS total_qty '
            'FROM "tblRestockRequest" r JOIN "tblSupplier" p ON p."id" = r."supplierId" '
            'JOIN "tblStockLocation" k ON k."id" = r."stockLocationId" '
            'WHERE (%s::text IS NULL OR r."status" = %s::text) '
            '  AND (%s::int IS NULL OR (r."supplierId" = %s::int AND r."status" <> \'draft\')) '
            'ORDER BY r."created_at" DESC',
            (status, status, sup_id, sup_id)).fetchall()
        return [_to_entity(RestockRequest, r) for r in rows]

    def get_restock_request_detail(self, request: RestockRequest) -> RestockRequest:
        row = self.con.execute(
            'SELECT r.*, p."name" AS supplier_name, k."name" AS location_name FROM "tblRestockRequest" r '
            'JOIN "tblSupplier" p ON p."id" = r."supplierId" JOIN "tblStockLocation" k ON k."id" = r."stockLocationId" '
            'WHERE r."id" = %s', (request.id,)).fetchone()
        if row is None:
            return request
        out = _to_entity(RestockRequest, row)
        rows = self.con.execute(
            'SELECT i.*, v."sku", v."colour", v."size_label", s."name" AS style_name, l."stockLocationId" AS variant_location_id '
            'FROM "tblRestockItem" i JOIN "tblProductVariant" v ON v."id" = i."productVariantId" '
            'JOIN "tblStyle" s ON s."id" = v."styleId" LEFT JOIN "tblStockLevel" l ON l."productVariantId" = v."id" '
            'WHERE i."restockRequestId" = %s ORDER BY i."id"', (request.id,)).fetchall()
        out.items = [_to_entity(RestockItem, r) for r in rows]
        return out

    def add_restock_request(self, request: RestockRequest, staff: StaffMember) -> bool:
        request.status = request.status or RestockStatus.DRAFT
        items = getattr(request, "items", [])
        if request.status not in (RestockStatus.DRAFT, RestockStatus.SENT) or not items \
                or any((i.quantity or 0) <= 0 for i in items):
            return False
        try:
            with self.con.transaction():
                no = _next_no(self.con, "RST", "tblRestockRequest", "request_no")
                row = self.con.execute(
                    'INSERT INTO "tblRestockRequest"("request_no","status","created_at","expected_date",'
                    '"supplierId","stockLocationId","staffMemberId") VALUES (%s,%s,now(),%s,%s,%s,%s) '
                    'RETURNING "id","created_at"',
                    (no, request.status.value, request.expected_date, request.supplierId, request.stockLocationId,
                     staff.id)).fetchone()
                self._insert_items(row["id"], items)
        except BUSINESS_ERRORS:
            return False
        request.id, request.request_no, request.created_at = row["id"], no, row["created_at"]
        request.staffMemberId = staff.id
        return True

    def update_restock_request(self, request: RestockRequest) -> bool:
        try:
            with self.con.transaction():
                old = self.con.execute('SELECT "status" FROM "tblRestockRequest" WHERE "id" = %s FOR UPDATE',
                                       (request.id,)).fetchone()
                if old is None:
                    raise _Abort()
                old_status = RestockStatus(old["status"])
                if request.status not in RESTOCK_NEXT[old_status] or request.status == RestockStatus.RECEIVED:
                    raise _Abort()          # nhận hàng đi qua receive_restock_request
                if (old_status == RestockStatus.SENT and request.status == RestockStatus.CANCELLED
                        and not (request.supplier_note or "").strip()):
                    raise _Abort()          # UC17 E1: từ chối phải có lý do
                self.con.execute(
                    'UPDATE "tblRestockRequest" SET "status"=%s,"expected_date"=%s,"supplier_note"=%s,"confirm_at"=%s,'
                    '"supplierId"=%s,"stockLocationId"=%s WHERE "id"=%s AND "status"=%s',
                    (request.status.value, request.expected_date, request.supplier_note, request.confirm_at,
                     request.supplierId, request.stockLocationId, request.id, old_status.value))
                if old_status == RestockStatus.DRAFT and hasattr(request, "items"):
                    if not request.items and request.status != RestockStatus.CANCELLED:
                        raise _Abort()
                    self.con.execute('DELETE FROM "tblRestockItem" WHERE "restockRequestId" = %s', (request.id,))
                    self._insert_items(request.id, request.items)
        except (_Abort, *BUSINESS_ERRORS):
            return False
        return True

    def receive_restock_request(self, request: RestockRequest, staff: StaffMember) -> bool:
        try:
            with self.con.transaction():
                head = self.con.execute('SELECT * FROM "tblRestockRequest" WHERE "id" = %s FOR UPDATE',
                                        (request.id,)).fetchone()
                if head is None or head["status"] != RestockStatus.CONFIRMED.value:
                    raise _Abort()
                items = self.con.execute(
                    'SELECT * FROM "tblRestockItem" WHERE "restockRequestId" = %s ORDER BY "productVariantId"',
                    (request.id,)).fetchall()
                for it in items:
                    level = self.con.execute(
                        'SELECT * FROM "tblStockLevel" WHERE "productVariantId" = %s FOR UPDATE',
                        (it["productVariantId"],)).fetchone()
                    if level is None or level["stockLocationId"] != head["stockLocationId"]:
                        raise _Abort()      # mỗi biến thể chỉ có một kho
                    self.con.execute('UPDATE "tblStockLevel" SET "on_hand" = "on_hand" + %s, '
                                     '"available" = "available" + %s WHERE "id" = %s',
                                     (it["quantity"], it["quantity"], level["id"]))
                    self.con.execute(
                        'INSERT INTO "tblStockMovement"("quantity_change","reason","reference","note","created_at",'
                        '"productVariantId","stockLocationId","staffMemberId") VALUES (%s,%s,%s,%s,now(),%s,%s,%s)',
                        (it["quantity"], MovementReason.RESTOCK.value, head["request_no"], "Nhận hàng nhập",
                         it["productVariantId"], level["stockLocationId"], staff.id))
                self.con.execute('UPDATE "tblRestockRequest" SET "status" = %s WHERE "id" = %s',
                                 (RestockStatus.RECEIVED.value, request.id))
        except _Abort:
            return False
        request.status = RestockStatus.RECEIVED
        return True

    def _insert_items(self, request_id: int, items: list[RestockItem]) -> None:
        merged: dict[int, int] = {}
        for i in items:
            merged[i.productVariantId] = merged.get(i.productVariantId, 0) + i.quantity
        for variant_id, qty in merged.items():
            self.con.execute('INSERT INTO "tblRestockItem"("quantity","restockRequestId","productVariantId") '
                             'VALUES (%s,%s,%s)', (qty, request_id, variant_id))
