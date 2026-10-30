"""ShipmentDAO — Kiện hàng (giao đi `outbound`, lấy về `return`) kèm ShipmentRecord, ShipmentEvent."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _to_entity, _val
from abc_fashion.model.fulfilment import ShipmentDirection, ShipmentStatus, Shipment, ShipmentEvent, ShipmentRecord
from abc_fashion.model.sales import Order


class ShipmentDAO(DAO):
    """Bảng tblShipment. Dùng bởi: ManageOrderFrm, ProcessReturnFrm, TrackShipmentFrm; OrderDAO."""

    def get_shipment_by_order(self, order: Order) -> list[Shipment]:
        rows = self.con.execute(
            'SELECT sh.*, k."name" AS location_name FROM "tblShipment" sh '
            'JOIN "tblStockLocation" k ON k."id" = sh."stockLocationId" WHERE sh."orderId" = %s ORDER BY sh."id"',
            (order.id,)).fetchall()
        shipments = [_to_entity(Shipment, r) for r in rows]
        self._attach_records(shipments)
        return shipments

    def get_shipment_event(self, shipment: Shipment) -> list[ShipmentEvent]:
        rows = self.con.execute('SELECT * FROM "tblShipmentEvent" WHERE "shipmentId" = %s ORDER BY "occurred_at", "id"',
                                (shipment.id,)).fetchall()
        return [_to_entity(ShipmentEvent, r) for r in rows]

    def update_shipment(self, shipment: Shipment) -> bool:
        if shipment.status == ShipmentStatus.DELIVERED and shipment.delivered_at is None:
            row = self.con.execute('SELECT localtimestamp(0) AS t').fetchone()
            shipment.delivered_at = row["t"]
        n = self.con.execute(
            'UPDATE "tblShipment" SET "carrier"=%s,"tracking_no"=%s,"status"=%s,"delivered_at"=%s WHERE "id"=%s',
            (shipment.carrier, shipment.tracking_no, _val(shipment.status), shipment.delivered_at,
             shipment.id)).rowcount
        return n == 1

    def add_shipment_event(self, event: ShipmentEvent, shipment: Shipment) -> bool:
        """Thêm sự kiện và đặt trạng thái kiện theo sự kiện mới nhất; bỏ qua sự kiện trùng."""
        with self.con.transaction():
            # không dùng ON CONFLICT: CSDL tạo từ báo cáo không có UNIQUE (shipmentId, status, occurred_at)
            row = self.con.execute(
                'INSERT INTO "tblShipmentEvent"("status","occurred_at","note","shipmentId") '
                'SELECT %s, t, %s, %s FROM (SELECT coalesce(%s::timestamp, localtimestamp(0)) AS t) x '
                'WHERE NOT EXISTS (SELECT 1 FROM "tblShipmentEvent" e WHERE e."shipmentId" = %s '
                '  AND e."status" = %s AND e."occurred_at" = x.t) RETURNING "id"',
                (_val(event.status), event.note, shipment.id, event.occurred_at, shipment.id,
                 _val(event.status))).fetchone()
            if row is None:
                return False
            latest = self.con.execute(
                'SELECT "status","occurred_at" FROM "tblShipmentEvent" WHERE "shipmentId" = %s '
                'ORDER BY "occurred_at" DESC, "id" DESC LIMIT 1', (shipment.id,)).fetchone()
            self.con.execute(
                'UPDATE "tblShipment" SET "status" = %s, '
                '"delivered_at" = CASE WHEN %s = \'delivered\' THEN coalesce("delivered_at", %s) ELSE "delivered_at" END '
                'WHERE "id" = %s', (latest["status"], latest["status"], latest["occurred_at"], shipment.id))
        event.id, event.shipmentId = row["id"], shipment.id
        shipment.status = ShipmentStatus(latest["status"])
        if shipment.status == ShipmentStatus.DELIVERED and shipment.delivered_at is None:
            shipment.delivered_at = latest["occurred_at"]
        return True

    def add_shipment(self, shipment: Shipment, order: Order) -> bool:
        records: list[ShipmentRecord] = getattr(shipment, "records", [])
        if shipment.direction == ShipmentDirection.RETURN and shipment.returnRequestId is None:
            return False
        try:
            with self.con.transaction():
                row = self.con.execute(
                    'INSERT INTO "tblShipment"("direction","carrier","service_level","tracking_no","fee","status",'
                    '"orderId","stockLocationId","returnRequestId") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING "id"',
                    (_val(shipment.direction), shipment.carrier, _val(shipment.service_level), shipment.tracking_no,
                     shipment.fee or 0, _val(shipment.status or ShipmentStatus.REQUESTED), order.id,
                     shipment.stockLocationId, shipment.returnRequestId)).fetchone()
                for rec in records:
                    rec.id = self.con.execute(
                        'INSERT INTO "tblShipmentRecord"("quantity","shipmentId","orderItemId") VALUES (%s,%s,%s) '
                        'RETURNING "id"', (rec.quantity, row["id"], rec.orderItemId)).fetchone()["id"]
                    rec.shipmentId = row["id"]
        except BUSINESS_ERRORS:
            return False
        shipment.id, shipment.orderId = row["id"], order.id
        shipment.status = shipment.status or ShipmentStatus.REQUESTED
        return True

    def _get_open_shipments(self) -> list[Shipment]:
        """Kiện đã có mã vận đơn và chưa kết thúc — đối tượng của bộ đồng bộ vận chuyển nền."""
        rows = self.con.execute('SELECT * FROM "tblShipment" WHERE "tracking_no" IS NOT NULL AND "status" IN '
                                '(\'requested\',\'picked_up\',\'in_transit\') ORDER BY "id"').fetchall()
        return [_to_entity(Shipment, r) for r in rows]

    def _attach_records(self, shipments: list[Shipment]) -> None:
        if not shipments:
            return
        rows = self.con.execute(
            'SELECT r.*, v."sku", s."name" AS style_name FROM "tblShipmentRecord" r '
            'JOIN "tblOrderItem" oi ON oi."id" = r."orderItemId" '
            'JOIN "tblProductVariant" v ON v."id" = oi."productVariantId" JOIN "tblStyle" s ON s."id" = v."styleId" '
            'WHERE r."shipmentId" = ANY(%s) ORDER BY r."id"', ([s.id for s in shipments],)).fetchall()
        by_ship: dict[int, list[ShipmentRecord]] = {s.id: [] for s in shipments}
        for r in rows:
            by_ship[r["shipmentId"]].append(_to_entity(ShipmentRecord, r))
        for s in shipments:
            s.records = by_ship[s.id]
