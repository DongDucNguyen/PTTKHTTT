"""Giao diện ở chế độ http với các dịch vụ mô phỏng (external_services/): kịch bản trình diễn chạy qua ngân hàng,
hãng vận chuyển, dịch vụ e-mail thật sự; và các ca dịch vụ ngoài lỗi giữa chừng (mục 7.2 KE_HOACH_MOCK_SERVERS.md):
nghiệp vụ không được hỏng dữ liệu, không tạo trùng, và làm lại được khi dịch vụ sống lại.

Cần CSDL thử (ABC_FASHION_TEST_DSN) và dịch vụ mô phỏng (tự khởi động như test_external.py).
"""
from __future__ import annotations

from tkinter import messagebox

import pytest

from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.control.gateway import _http
from abc_fashion.model.catalogue import Style
from abc_fashion.model.fulfilment import ShipmentDirection, ShipmentStatus
from abc_fashion.model.returns import InspectionResult, ReturnStatus, ReturnRequest
from abc_fashion.model.sales import OrderStatus, PaymentMethodType, net_paid, Order
from abc_fashion.model.user import User
from test_external import external, http_mode  # noqa: F401 - fixture dùng chung
from test_views import newest, staff, ui  # noqa: F401 - fixture dùng chung
from test_views import test_demo_scenario_end_to_end as _demo


def _calls(service: str, path: str) -> list[dict]:
    return _http.call(service, "GET", f"/__admin/calls?limit=500&path_contains={path}")[1]["calls"]


def _fail_next(service: str, n: int = 1, status: int = 503) -> None:
    _http.call(service, "POST", "/__admin/behavior", {"fail_next": n, "status": status})


@pytest.fixture(autouse=True)
def fresh_services(external):
    """CSDL thử tạo lại mỗi test nên số đơn lặp lại; xoá luôn trạng thái các dịch vụ mô phỏng cho khớp."""
    for s in ("payment", "shipping", "notify"):
        _http.call(s, "POST", "/__admin/reset")


@pytest.fixture()
def warnings(ui, monkeypatch):
    """Ca lỗi có chủ đích: gom hộp cảnh báo / lỗi riêng để test kiểm tra, không làm fixture `ui` báo lỗi."""
    box: list[str] = []
    monkeypatch.setattr(messagebox, "showwarning", lambda *a, **k: box.append(" | ".join(map(str, a))))
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: box.append("error: " + " | ".join(map(str, a))))
    return box


def _customer():
    from abc_fashion.control.dao.customer_dao import CustomerDAO
    return CustomerDAO().get_customer_by_user(User(id=10))                  # an.nguyen@gmail.com, thẻ 4242 / 0002


def _checkout(ui, customer, last4: str = "4242"):
    """Thêm 1 áo vào giỏ, sang thanh toán, chọn thẻ `last4`; trả CheckoutFrm chưa đặt."""
    from abc_fashion.view.catalogue.style_detail_frm import StyleDetailFrm
    from abc_fashion.view.checkout.cart_frm import CartFrm
    from abc_fashion.view.checkout.checkout_frm import CheckoutFrm

    d = StyleDetailFrm(customer, Style(id=1))
    d.cbo_colour.set("Trắng")
    d._on_colour()
    d.cbo_size.set("M")
    d.on_select_variant()
    d.spn_quantity.set(1)
    d.on_add_to_cart()
    CartFrm(customer).on_checkout()
    co = newest(ui, CheckoutFrm)
    co.var_payment_method.set(PaymentMethodType.CARD.value)
    co._on_change_payment_method()
    co.cbo_linked_method.current(next(i for i, v in enumerate(co.cbo_linked_method._values)
                                      if v.masked_number.endswith(last4)))
    return co


def _order_count(db) -> int:
    return db.execute('SELECT count(*) AS n FROM "tblOrder"').fetchone()["n"]


# ---------------------------------------------------------------- kịch bản trình diễn qua dịch vụ thật sự
def test_demo_scenario_over_http(ui, db, http_mode):
    _demo(ui, db)
    no = db.execute('SELECT "order_no" FROM "tblOrder" ORDER BY "id" DESC LIMIT 1').fetchone()["order_no"]
    tx = _http.call("payment", "GET", f"/v1/transactions?reference={no}")[1]["transactions"]
    seen = sorted((t["kind"], t["status"], t["last4"]) for t in tx)
    assert seen == [("charge", "declined", "0002"), ("charge", "succeeded", "4242"), ("refund", "succeeded", "4242")]
    refs = {p["transaction_ref"] for p in db.execute('SELECT "transaction_ref" FROM "tblPayment" p JOIN "tblOrder" o '
                                                     'ON o."id" = p."orderId" WHERE o."order_no" = %s', (no,)).fetchall()}
    assert {t["ref"] for t in tx} == refs                         # CSDL lưu đúng mã giao dịch của ngân hàng
    created = [c for c in _calls("shipping", "/v1/shipments") if c["method"] == "POST" and c["path"] == "/v1/shipments"]
    assert len(created) == 3                                                   # 2 kiện giao + 1 kiện lấy hàng trả
    trackings = {r["tracking_no"] for r in db.execute(
        'SELECT "tracking_no" FROM "tblShipment" s JOIN "tblOrder" o ON o."id" = s."orderId" WHERE o."order_no" = %s',
        (no,)).fetchall()}
    assert len(trackings) == 3 and all(t[:3] in ("GHT", "GHN") and t[4:].isdigit() for t in trackings)
    events = {m["event_type"] for m in _http.call("notify", "GET", "/v1/messages?to=an.nguyen")[1]["messages"]}
    assert {"order_confirmed", "return_authorised", "refund_completed"} <= events
    assert db.execute('SELECT count(*) AS n FROM "tblNotification" WHERE "status" <> \'sent\'').fetchone()["n"] == 0


# ---------------------------------------------------------------- ngân hàng lỗi
def test_bank_down_at_checkout_keeps_one_order_and_retry_pays(ui, db, http_mode, warnings):
    from abc_fashion.view.checkout.confirm_order_frm import ConfirmOrderFrm

    customer, before = _customer(), _order_count(db)
    co = _checkout(ui, customer)
    _fail_next("payment")
    co.on_place_order()
    assert warnings and "thanh toán lại" in warnings[0]
    conf = newest(ui, ConfirmOrderFrm)
    assert conf.order.status == OrderStatus.PENDING_PAYMENT and _order_count(db) == before + 1
    assert not co.winfo_exists()                                               # không thể bấm "Đặt hàng" lần hai
    assert OrderDAO().get_order_detail(conf.order).payments == []              # chưa thu, chưa ghi giao dịch
    conf.cbo_method.current(next(i for i, v in enumerate(conf.cbo_method._values)
                                 if v[1] and v[1].masked_number.endswith("4242")))
    conf.on_retry_payment()
    assert conf.order.status == OrderStatus.CONFIRMED and _order_count(db) == before + 1
    assert [t["status"] for t in _http.call("payment", "GET", f"/v1/transactions?reference={conf.order.order_no}")[1]
            ["transactions"]] == ["succeeded"]


def test_bank_slow_but_in_time(ui, db, http_mode):
    _http.call("payment", "POST", "/__admin/behavior", {"latency_ms": 1500})
    try:
        co = _checkout(ui, _customer())
        co.on_place_order()
    finally:
        _http.call("payment", "POST", "/__admin/behavior", {"latency_ms": 0})
    from abc_fashion.view.checkout.confirm_order_frm import ConfirmOrderFrm
    assert newest(ui, ConfirmOrderFrm).order.status == OrderStatus.CONFIRMED


def test_bank_down_at_cancel_records_failed_refund_then_staff_refunds(ui, db, http_mode, warnings):
    from abc_fashion.view.order_admin.manage_order_frm import ManageOrderFrm

    mo = ManageOrderFrm(staff(db, 2), OrderDAO().get_order_detail(Order(id=3)))     # đã thu 590.000 đ bằng thẻ
    mo.txt_cancel_reason.insert(0, "Khách đổi ý")
    _fail_next("payment")
    mo.on_cancel_order()
    assert len(warnings) == 1 and "chưa hoàn được tiền" in warnings[0]
    order = OrderDAO().get_order_detail(Order(id=3))
    assert order.status == OrderStatus.CANCELLED and net_paid(order.payments) == 590_000
    assert [(p.kind.value, p.status.value) for p in order.payments][-1] == ("refund", "failed")
    assert str(mo.btn_refund.cget("state")) != "disabled"
    mo.on_refund()                                                              # dịch vụ sống lại: hoàn từ màn hình quản lý
    assert net_paid(OrderDAO().get_order_detail(Order(id=3)).payments) == 0
    assert any(m["event_type"] == "order_cancelled" for m in
               _http.call("notify", "GET", "/v1/messages?to=an.nguyen")[1]["messages"])


# ---------------------------------------------------------------- hãng vận chuyển lỗi
def test_carrier_down_at_dispatch_changes_nothing_then_retry(ui, db, http_mode, warnings):
    from abc_fashion.view.order_admin.manage_order_frm import ManageOrderFrm

    mo = ManageOrderFrm(staff(db, 2), OrderDAO().get_order_detail(Order(id=3)))
    mo.cbo_new_status.select_value(OrderStatus.PROCESSING)
    mo.on_update_status()
    mo.cbo_new_status.select_value(OrderStatus.SHIPPED)
    _fail_next("shipping")
    mo.on_update_status()
    assert len(warnings) == 1 and warnings[0].startswith("error:")             # hộp "Lỗi hệ thống"
    order = OrderDAO().get_order_detail(Order(id=3))
    assert order.status == OrderStatus.PROCESSING
    assert [(s.status, s.tracking_no) for s in order.shipments] == [(ShipmentStatus.REQUESTED, None)]
    mo._reload()
    mo.cbo_new_status.select_value(OrderStatus.SHIPPED)
    mo.on_update_status()
    order = OrderDAO().get_order_detail(Order(id=3))
    assert order.status == OrderStatus.SHIPPED and order.shipments[0].tracking_no.startswith("GHTK")


def test_carrier_down_at_return_pickup_reuses_the_shipment(ui, db, http_mode, warnings):
    from abc_fashion.view.returns.process_return_frm import ProcessReturnFrm

    rid = _return_request(db)
    pr = ProcessReturnFrm(staff(db, 5), ReturnRequest(id=rid))
    pr.on_authorise()
    _fail_next("shipping")
    pr.on_create_pickup()
    assert len(warnings) == 1 and warnings[0].startswith("error:")
    pr._reload()
    assert pr.return_request.status == ReturnStatus.AUTHORISED
    pr.on_create_pickup()
    r = ReturnRequestDAO().get_return_request_detail(ReturnRequest(id=rid))
    returns = [s for s in r.shipments if s.direction == ShipmentDirection.RETURN]
    assert r.status == ReturnStatus.IN_TRANSIT and len(returns) == 1           # không tạo kiện lấy hàng thứ hai
    assert returns[0].status == ShipmentStatus.PICKED_UP and returns[0].tracking_no


def test_carrier_down_at_exchange_does_not_deduct_stock_twice(ui, db, http_mode, warnings):
    from abc_fashion.view.returns.inspect_return_frm import InspectReturnFrm
    from abc_fashion.view.returns.process_return_frm import ProcessReturnFrm

    rid = _return_request(db, exchange_to=4)                                   # W002 đỏ M → xanh M
    cs, wh = staff(db, 5), staff(db, 6)
    pr = ProcessReturnFrm(cs, ReturnRequest(id=rid))
    pr.on_authorise()
    pr.on_create_pickup()
    ins = InspectReturnFrm(wh, ReturnRequest(id=rid))
    ins.tbl_return_item.selection_set(str(ins.return_request.items[0].id))
    ins.cbo_inspection_result.select_value(InspectionResult.PASSED)
    ins.on_save_inspection()
    ins.on_finish()
    stock = lambda: db.execute('SELECT "on_hand" FROM "tblStockLevel" WHERE "productVariantId" = 4').fetchone()["on_hand"]
    before = stock()
    pr = ProcessReturnFrm(cs, ReturnRequest(id=rid))
    _fail_next("shipping")
    pr.on_ship_replacement()
    assert len(warnings) == 1 and warnings[0].startswith("error:")
    assert stock() == before - 1
    pr._reload()
    pr.on_ship_replacement()                                                    # hãng sống lại: chỉ bàn giao kiện đã tạo
    r = ReturnRequestDAO().get_return_request_detail(ReturnRequest(id=rid))
    outbound = [s for s in r.shipments if s.direction == ShipmentDirection.OUTBOUND]
    assert r.status == ReturnStatus.EXCHANGED and stock() == before - 1
    assert len(outbound) == 1 and outbound[0].tracking_no and outbound[0].status == ShipmentStatus.PICKED_UP


def _return_request(db, exchange_to: int | None = None) -> int:
    """Yêu cầu trả 1 món của đơn 2 (đã giao, khách Bình) qua ReturnRequestFrm; trả id."""
    from abc_fashion.control.dao.customer_dao import CustomerDAO
    from abc_fashion.view.order.return_request_frm import ReturnRequestFrm

    db.execute('UPDATE "tblShipment" SET "delivered_at" = localtimestamp WHERE "orderId" = 2')   # trong hạn đổi trả
    order = OrderDAO().get_order_detail(Order(id=2))
    item = next(i for i in order.items if i.productVariantId == 3)                       # W002-RED-M
    rr = ReturnRequestFrm(CustomerDAO().get_customer_by_user(User(id=11)), order)
    rr.tbl_order_item.selection_set(str(item.id))
    if exchange_to:
        rr.var_return_type.set("exchange")
        rr._on_type()
        rr.cbo_replacement.current(next(i for i, v in enumerate(rr.cbo_replacement._values) if v.id == exchange_to))
    rr.cbo_reason_code.current(1)
    rr.on_select_item()
    rr.on_submit()
    return ReturnRequestDAO().get_return_request_by_order(order).id


# ---------------------------------------------------------------- e-mail lỗi, liên kết thẻ, tìm kiếm AI tắt
def test_notify_down_does_not_block_business(ui, db, http_mode, monkeypatch):
    from abc_fashion.view.order.cancel_request_frm import CancelRequestFrm

    monkeypatch.setenv("ABC_FASHION_NOTIFY_URL", "http://127.0.0.1:9")
    cr = CancelRequestFrm(OrderDAO().get_order_detail(Order(id=3)))
    cr.cbo_reason.current(0)
    cr.on_send()
    order = OrderDAO().get_order_detail(Order(id=3))
    assert order.status == OrderStatus.CANCELLED and net_paid(order.payments) == 0
    rows = db.execute('SELECT "event_type", "status" FROM "tblNotification" WHERE "message" LIKE %s '
                      'AND "event_type" <> %s', ("%ORD-261020-001%", "order_confirmed")).fetchall()
    assert {r["event_type"] for r in rows} == {"order_cancelled", "refund_completed"}
    assert {r["status"] for r in rows} == {"failed"}                           # ghi lại, không chặn huỷ / hoàn tiền


def test_link_payment_method_opens_bank_account(ui, db, http_mode):
    from abc_fashion.view.account.link_payment_method_frm import LinkPaymentMethodFrm

    customer = _customer()
    lf = LinkPaymentMethodFrm(customer)
    lf.cbo_provider.current(1)                                                  # Mastercard
    lf.on_link()
    row = db.execute('SELECT * FROM "tblPaymentMethod" WHERE "customerId" = %s ORDER BY "id" DESC LIMIT 1',
                     (customer.id,)).fetchone()
    assert row["provider"] == "Mastercard" and row["masked_number"].startswith("**** ")
    acc = _http.call("payment", "GET", f"/v1/accounts/{row['masked_number'][-4:]}")[1]
    assert acc["status"] == "active" and acc["provider"] == "Mastercard"
    co = _checkout(ui, customer, row["masked_number"][-4:])                     # thanh toán được bằng thẻ vừa liên kết
    co.on_place_order()
    from abc_fashion.view.checkout.confirm_order_frm import ConfirmOrderFrm
    assert newest(ui, ConfirmOrderFrm).order.status == OrderStatus.CONFIRMED


def test_search_by_image_with_ai_down_suggests_text(ui, db, monkeypatch, tmp_path):
    import time
    from tkinter import filedialog

    from abc_fashion.view.catalogue.search_style_frm import SearchStyleFrm

    monkeypatch.setenv("ABC_FASHION_GATEWAY_MODE", "http")
    monkeypatch.setenv("ABC_FASHION_AI_URL", "http://127.0.0.1:9")
    img = tmp_path / "q.jpg"
    img.write_bytes(b"\xff\xd8\xff")
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **k: str(img))
    monkeypatch.setattr("abc_fashion.view.catalogue.search_style_frm.show_image", lambda *a, **k: None)
    sf = SearchStyleFrm(_customer(), "")
    sf.on_search_by_image()
    assert "disabled" in sf.btn_search.state()                                  # đang chờ luồng phụ
    deadline = time.time() + 15
    while time.time() < deadline and "disabled" in sf.btn_search.state():
        ui.update()
        time.sleep(0.05)
    assert "Hãy tìm bằng chữ" in sf.lbl_message.cget("text") and sf.list_style == []
    sf.txt_keyword.insert(0, "áo")
    sf.on_search()
    assert sf.list_style                                                        # tìm bằng chữ vẫn dùng được
