"""Kiểm thử DAO trên CSDL thử (mục 14.2). Mỗi test chạy trên schema + seed mới (fixture `db`)."""
from __future__ import annotations

import multiprocessing as mp
from datetime import date

import pytest

from abc_fashion.control.dao.cart_dao import CartDAO
from abc_fashion.control.dao.customer_dao import CustomerDAO
from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.restock_request_dao import RestockRequestDAO
from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.style_stat_dao import StyleStatDAO
from abc_fashion.control.dao.return_stat_dao import ReturnStatDAO
from abc_fashion.control.dao.user_dao import UserDAO
from abc_fashion.control.dao.voucher_dao import VoucherDAO
from abc_fashion.model.inventory import MovementReason, RestockStatus, RestockRequest, StockLevel, StockMovement
from abc_fashion.model.returns import Resolution, ReturnReason, ReturnType, ReturnItem, ReturnRequest
from abc_fashion.model.sales import (DeliveryService, OrderStatus, recalc_order, CartItem, Order, OrderItem)
from abc_fashion.model.user import Customer, StaffMember, User

AN, BINH = Customer(id=1, userId=10), Customer(id=2, userId=11)
PRICES = {1: 450_000, 2: 450_000, 3: 690_000, 4: 690_000, 5: 250_000, 6: 250_000, 7: 590_000, 8: 590_000}
STYLE_OF = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4}


def make_order(lines: dict[int, int], vouchers=()) -> Order:
    o = Order(delivery_service=DeliveryService.STANDARD, ship_recipient="A", ship_phone="0900000000",
                 ship_address="1 Test")
    o.items = [OrderItem(productVariantId=v, quantity=q, unit_price=PRICES[v], discount=0, styleId=STYLE_OF[v])
               for v, q in lines.items()]
    o.vouchers = list(vouchers)
    recalc_order(o)
    return o


def level(con, variant_id):
    return con.execute('SELECT * FROM "tblStockLevel" WHERE "productVariantId" = %s', (variant_id,)).fetchone()


def count(con, table):
    return con.execute(f'SELECT count(*) AS n FROM "{table}"').fetchone()["n"]


def assert_ledger(con):
    rows = con.execute(
        'SELECT l."productVariantId", l."on_hand", coalesce(sum(m."quantity_change"), 0) AS s '
        'FROM "tblStockLevel" l LEFT JOIN "tblStockMovement" m ON m."productVariantId" = l."productVariantId" '
        'GROUP BY l."productVariantId", l."on_hand"').fetchall()
    assert all(r["on_hand"] == r["s"] for r in rows), rows


# ---------------------------------------------------------------- tài khoản
def test_login_rehashes_plaintext_and_rejects_bad(db):
    dao = UserDAO()
    u = User(email="AN.NGUYEN@gmail.com", password="abc12345")
    assert dao.check_login(u) and u.id == 10 and u.password is None
    stored = db.execute('SELECT "password" FROM "tblUser" WHERE "id" = 10').fetchone()["password"]
    assert stored.startswith("pbkdf2$")
    assert dao.check_login(User(email="an.nguyen@gmail.com", password="abc12345"))
    assert not dao.check_login(User(email="an.nguyen@gmail.com", password="sai"))
    assert not dao.check_login(User(email="khoa.le@gmail.com", password="abc12345"))       # suspended
    assert not dao.check_login(User(email="khong.co@gmail.com", password="abc12345"))


def test_email_used_case_insensitive(db):
    assert UserDAO().is_email_used("Admin@ABC.vn")
    assert not UserDAO().is_email_used("moi@abc.vn")


def test_register_creates_user_customer_cart(db):
    before = (count(db, "tblUser"), count(db, "tblCustomer"), count(db, "tblCart"))
    c = Customer(email="moi@abc.vn", password="matkhau123", full_name="Người Mới", phone="0911111111",
                    preferred_colours=["Đen", "Đỏ"])
    assert CustomerDAO().add_customer(c) and c.id and c.userId
    assert (count(db, "tblUser"), count(db, "tblCustomer"), count(db, "tblCart")) == tuple(n + 1 for n in before)
    again = Customer(email="MOI@abc.vn", password="matkhau123", full_name="X", phone="0911111112")
    assert not CustomerDAO().add_customer(again)
    assert count(db, "tblUser") == before[0] + 1                                           # không để lại dòng nào
    loaded = CustomerDAO().get_customer_by_user(User(id=c.userId))
    assert loaded.preferred_colours == ["Đen", "Đỏ"] and loaded.email == "moi@abc.vn"


# ---------------------------------------------------------------- tồn kho
def test_check_availability_and_adjust_not_negative(db):
    dao = StockLevelDAO()
    bad = dao.check_availability([CartItem(productVariantId=8, quantity=2), CartItem(productVariantId=1, quantity=1)])
    assert [b.productVariantId for b in bad] == [8]
    l8 = StockLevel(id=level(db, 8)["id"])
    assert not dao.adjust_stock(l8, StockMovement(quantity_change=-2, reason=MovementReason.ADJUSTMENT, staffMemberId=6))
    assert dao.adjust_stock(l8, StockMovement(quantity_change=+4, reason=MovementReason.ADJUSTMENT,
                                                 reference="KK-1", note="kiểm kê", staffMemberId=6))
    assert level(db, 8)["on_hand"] == 5 and level(db, 8)["available"] == 5
    assert_ledger(db)


# ---------------------------------------------------------------- đặt hàng
def test_order_one_location_one_shipment_and_cart_cleared(db):
    cart = CartDAO().get_cart_by_customer(AN)
    assert CartDAO().add_cart_item(cart, CartItem(productVariantId=1, quantity=1))
    o = make_order({1: 1, 5: 2})
    assert OrderDAO().add_order(o, AN) and o.order_no.startswith("ORD-")
    assert count(db, "tblShipment") == 5 + 1
    assert level(db, 1)["reserved"] == 1 and level(db, 1)["available"] == 19 and level(db, 1)["on_hand"] == 20
    assert CartDAO().get_cart_by_customer(AN).items == []


def test_order_two_locations_two_shipments(db):
    o = make_order({1: 1, 3: 1})
    o.shipping_fee = 0
    assert OrderDAO().add_order(o, AN)
    ships = db.execute('SELECT * FROM "tblShipment" WHERE "orderId" = %s ORDER BY "id"', (o.id,)).fetchall()
    assert len(ships) == 2 and {s["stockLocationId"] for s in ships} == {1, 2}
    recs = db.execute('SELECT count(*) AS n FROM "tblShipmentRecord" r JOIN "tblShipment" s ON s."id" = r."shipmentId" '
                      'WHERE s."orderId" = %s', (o.id,)).fetchone()["n"]
    assert recs == 2


def test_order_with_used_up_voucher_rolls_back(db):
    orders, l1 = count(db, "tblOrder"), level(db, 1)
    voucher = VoucherDAO().get_voucher_by_code("hetluot")
    o = make_order({1: 1}, [voucher])
    assert not OrderDAO().add_order(o, AN) and o.id is None
    assert count(db, "tblOrder") == orders and level(db, 1) == l1


def test_confirm_then_cancel_restores_stock_and_voucher(db):
    voucher = VoucherDAO().get_voucher_by_code("XUANHE10")
    o = make_order({1: 2}, [voucher])
    dao = OrderDAO()
    assert dao.add_order(o, AN)
    assert db.execute('SELECT "used_count" FROM "tblVoucher" WHERE "id" = 1').fetchone()["used_count"] == 1
    o.status = OrderStatus.CONFIRMED
    assert dao.update_order_status(o)
    l1 = level(db, 1)
    assert (l1["on_hand"], l1["reserved"], l1["available"]) == (18, 0, 18)
    o.status = OrderStatus.DELIVERED                                                         # chuyển sai
    assert not dao.update_order_status(o) and o.status == OrderStatus.CONFIRMED
    o.cancel_reason = "Đổi ý"
    assert dao.cancel_order(o)
    l1 = level(db, 1)
    assert (l1["on_hand"], l1["reserved"], l1["available"]) == (20, 0, 20)
    assert db.execute('SELECT "used_count" FROM "tblVoucher" WHERE "id" = 1').fetchone()["used_count"] == 0
    assert_ledger(db)


def test_pending_cancel_releases_reservation(db):
    o = make_order({8: 1})
    assert OrderDAO().add_order(o, AN)
    assert level(db, 8)["available"] == 0
    o.cancel_reason = "Quá hạn"
    assert OrderDAO().cancel_order(o)
    assert (level(db, 8)["reserved"], level(db, 8)["available"]) == (0, 1)


def test_cannot_cancel_after_shipping(db):
    dao, o = OrderDAO(), Order(id=3)
    for st in (OrderStatus.PROCESSING, OrderStatus.SHIPPED):
        o.status = st
        assert dao.update_order_status(o)
    o.cancel_reason = "muộn"
    assert not dao.cancel_order(o)


def _buy_last(dsn: str, customer_id: int, q):
    from abc_fashion.control.dao import dao as dao_mod
    from abc_fashion.control.dao.order_dao import OrderDAO as _OrderDAO
    dao_mod.DSN = dsn
    q.put(_OrderDAO().add_order(make_order({8: 1}), Customer(id=customer_id)))


def test_two_buyers_last_item_only_one_wins(db, test_dsn):
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    procs = [ctx.Process(target=_buy_last, args=(test_dsn, cid, q)) for cid in (1, 2)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(60)
    results = sorted([q.get(timeout=5), q.get(timeout=5)])
    assert results == [False, True]
    assert (level(db, 8)["reserved"], level(db, 8)["available"]) == (1, 0)


# ---------------------------------------------------------------- trả hàng, nhập hàng, báo cáo
def test_second_return_request_for_same_order_refused(db):
    db.execute('UPDATE "tblShipment" SET "delivered_at" = now() - interval \'1 day\' WHERE "orderId" = 2')
    dao, order = ReturnRequestDAO(), Order(id=2)

    def request():
        r = ReturnRequest(return_type=ReturnType.RETURN, reason_code=ReturnReason.TOO_LARGE,
                             desired_resolution=Resolution.REFUND)
        r.items, r.evidence = [ReturnItem(orderItemId=3, quantity=1)], []
        return r
    assert dao.add_return_request(request(), order)
    assert not dao.add_return_request(request(), order)
    too_many = request()
    too_many.items[0].quantity = 5
    assert not ReturnRequestDAO().add_return_request(too_many, Order(id=1))              # đơn 1 đã có yêu cầu


def test_receive_restock_updates_stock_and_ledger(db):
    dao = RestockRequestDAO()
    r = dao.get_restock_request_detail(RestockRequest(id=1))
    r.status, r.confirm_at, r.expected_date = RestockStatus.CONFIRMED, date.today(), date.today()
    assert dao.update_restock_request(r)
    assert dao.receive_restock_request(r, StaffMember(id=6))
    assert level(db, 8)["on_hand"] == 21
    assert not dao.receive_restock_request(r, StaffMember(id=6))                          # đã nhận rồi
    assert_ledger(db)


def test_reports_have_data(db):
    stats = StyleStatDAO().get_style_stat(date(2026, 9, 1), date(2026, 10, 31), None, None)
    assert sum(s.revenue for s in stats) == 950_000 + 1_140_000 + 590_000
    returns = {s.code: s for s in ReturnStatDAO().get_return_stat(date(2026, 9, 1), date(2026, 10, 31), None)}
    assert returns["ST-M001"].quantity_returned == 1 and returns["ST-M001"].main_reason == ReturnReason.TOO_SMALL


def test_seed_ledger_is_consistent(db):
    assert_ledger(db)


def test_shipment_event_duplicate_skipped_and_status_follows(db):
    from datetime import datetime
    from abc_fashion.control.dao.shipment_dao import ShipmentDAO
    from abc_fashion.model.fulfilment import ShipmentStatus, Shipment, ShipmentEvent
    s, t = Shipment(id=5, status=ShipmentStatus.REQUESTED), datetime(2026, 10, 21, 9, 0)
    dao = ShipmentDAO()
    assert dao.add_shipment_event(ShipmentEvent(status=ShipmentStatus.PICKED_UP, occurred_at=t), s)
    assert not dao.add_shipment_event(ShipmentEvent(status=ShipmentStatus.PICKED_UP, occurred_at=t), s)
    assert dao.add_shipment_event(ShipmentEvent(status=ShipmentStatus.IN_TRANSIT, occurred_at=None), s)
    assert s.status == ShipmentStatus.IN_TRANSIT and len(dao.get_shipment_event(s)) == 2
