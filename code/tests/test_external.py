"""Gateway ở chế độ http ↔ các dịch vụ bên ngoài (external_services/). Tự khởi động dịch vụ nền nếu chưa chạy;
không khởi động được thì bỏ qua. Dịch vụ AI (thật) có file test riêng: test_ai_service.py."""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request

import pytest

from abc_fashion.control.gateway import _http
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.model.customer_data import Channel, LinkedMethodType, NotificationEvent, Notification, PaymentMethod
from abc_fashion.model.fulfilment import ShipmentDirection, ShipmentStatus, Shipment
from abc_fashion.model.sales import DeliveryService, Order, Payment
from abc_fashion.model.user import Customer
from conftest import CODE_DIR

EXTERNAL = os.path.join(os.path.dirname(CODE_DIR), "external_services")


def _up(service: str) -> bool:
    try:
        urllib.request.urlopen(_http.base_url(service) + "/health", timeout=2).read()
        return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def external():
    if not all(_up(s) for s in ("payment", "shipping", "notify")):
        manage = os.path.join(EXTERNAL, "manage.py")
        if os.path.exists(manage):
            subprocess.run([sys.executable, manage, "start", "payment", "shipping", "notify"], capture_output=True, timeout=120)
    if not all(_up(s) for s in ("payment", "shipping", "notify")):
        pytest.skip("Các dịch vụ mô phỏng chưa chạy (cd external_services && python manage.py setup && python manage.py start)")
    for s in ("payment", "shipping", "notify"):
        _http.call(s, "POST", "/__admin/reset")
    yield


@pytest.fixture()
def http_mode(external, monkeypatch):
    monkeypatch.setenv("ABC_FASHION_GATEWAY_MODE", "http")


def _order(no: str, amount: int) -> Order:
    return Order(order_no=no, grand_total=amount)


def _card(last4: str) -> PaymentMethod:
    return PaymentMethod(provider="Visa", method_type=LinkedMethodType.CARD, masked_number=f"**** {last4}")


# ---------------------------------------------------------------- thanh toán (ngân hàng)
def test_payment_pass_when_enough_balance_and_conditions(http_mode):
    gw = PaymentGateway()
    ok, ref = gw.charge(_order("T-OK", 500_000), _card("4242"))
    assert ok and ref.startswith("BANK-")
    assert gw.charge(_order("T-NOCARD", 300_000), None)[0]                       # chuyển khoản / ví chưa liên kết


def test_payment_declined_blocked_low_balance_and_too_large(http_mode):
    gw = PaymentGateway()
    assert not gw.charge(_order("T-0002", 100_000), _card("0002"))[0]            # tài khoản bị khoá (UC08 E2)
    assert not gw.charge(_order("T-9995", 500_000), _card("9995"))[0]            # số dư 100.000 đ không đủ
    assert gw.charge(_order("T-9995b", 90_000), _card("9995"))[0]                # đủ số dư thì qua
    assert not gw.charge(_order("T-BIG", 200_000_000), None)[0]                  # vượt hạn mức một giao dịch


def test_payment_refund_limits(http_mode):
    gw = PaymentGateway()
    _, ref = gw.charge(_order("T-REF", 1_000_000), _card("4242"))
    assert gw.refund(Payment(transaction_ref=ref, amount=600_000))[0]
    assert not gw.refund(Payment(transaction_ref=ref, amount=600_000))[0]     # vượt phần còn hoàn được
    assert gw.refund(Payment(transaction_ref=ref, amount=400_000))[0]
    assert gw.refund(Payment(transaction_ref="COD-ORD-1", amount=50_000))[0]  # giao dịch ngoài ngân hàng (COD) coi như qua


def test_link_method_returns_masked_number_only(http_mode):
    m = PaymentGateway().link_method(Customer(id=1), "card", "Visa")
    assert m.method_type == LinkedMethodType.CARD and m.customerId == 1
    assert m.masked_number.startswith("**** ") and len(m.masked_number) == 9 and m.masked_number[-4:].isdigit()
    assert PaymentGateway().charge(_order("T-LINK", 1_000_000), m)[0]            # tài khoản mới có số dư mặc định


def test_payment_unreachable_raises(monkeypatch):
    monkeypatch.setenv("ABC_FASHION_GATEWAY_MODE", "http")
    monkeypatch.setenv("ABC_FASHION_PAYMENT_URL", "http://127.0.0.1:9")
    with pytest.raises(_http.GatewayUnavailable):
        PaymentGateway().charge(_order("T-DOWN", 1000), None)


# ---------------------------------------------------------------- vận chuyển
def _shipment(id_: int, level=DeliveryService.STANDARD, address="1 Lê Lợi, Quận 1") -> Shipment:
    s = Shipment(id=id_, direction=ShipmentDirection.OUTBOUND, service_level=level, fee=0, status=ShipmentStatus.REQUESTED)
    s.to_address, s.from_location = address, "Kho Hà Nội"
    return s


def test_shipping_carrier_by_service_and_stable_history(http_mode):
    gw = ShippingGateway()
    s1, s2 = _shipment(901), _shipment(902, DeliveryService.EXPRESS)
    (c1, t1), (c2, t2) = gw.create_shipment(s1), gw.create_shipment(s2)
    assert (c1, t1[:4]) == ("GHTK", "GHTK") and (c2, t2[:3]) == ("GHN", "GHN")
    assert gw.create_shipment(s1) == (c1, t1)                                    # tạo lại cùng kiện: cùng vận đơn
    s1.tracking_no = t1
    first, second = gw.get_tracking(s1), gw.get_tracking(s1)
    assert [e.status for e in first] == [ShipmentStatus.REQUESTED]
    assert [(e.status, e.occurred_at) for e in first] == [(e.status, e.occurred_at) for e in second][:len(first)]


def test_shipping_advances_every_3_to_5_seconds_until_delivered(http_mode):
    gw, s = ShippingGateway(), _shipment(903)
    s.carrier, s.tracking_no = gw.create_shipment(s)
    started, seen = time.time(), {}
    while time.time() - started < 25:
        for e in gw.get_tracking(s):
            seen.setdefault(e.status, e.occurred_at)
        if ShipmentStatus.DELIVERED in seen:
            break
        time.sleep(0.5)
    order = [ShipmentStatus.REQUESTED, ShipmentStatus.PICKED_UP, ShipmentStatus.IN_TRANSIT, ShipmentStatus.DELIVERED]
    assert list(seen) == order
    gaps = [(seen[b] - seen[a]).total_seconds() for a, b in zip(order, order[1:])]
    assert all(2.5 <= g <= 5.5 for g in gaps), gaps                              # mỗi bước 3–5 giây (sai số làm tròn giây)


def test_shipping_failed_destination_and_unknown_tracking(http_mode):
    gw, s = ShippingGateway(), _shipment(904, address="9 Đường X, Quận FAIL, TP.HCM")
    s.carrier, s.tracking_no = gw.create_shipment(s)
    time.sleep(14)
    assert gw.get_tracking(s)[-1].status == ShipmentStatus.FAILED
    ghost = _shipment(905)
    ghost.tracking_no = "GHTK0000000"
    assert gw.get_tracking(ghost) == []                                          # vận đơn không do hãng tạo (dữ liệu cũ)


# ---------------------------------------------------------------- thông báo
def test_notification_delivered_bounced_and_unreachable(http_mode, monkeypatch):
    gw = NotificationGateway()

    def mail(to):
        n = Notification(channel=Channel.EMAIL, event_type=NotificationEvent.ORDER_CONFIRMED, message="Đơn đã xác nhận", customerId=1)
        n.recipient = to
        return n
    assert gw.send(mail("an.nguyen@gmail.com"))
    assert not gw.send(mail("x@bounce.test"))                                    # người nhận lỗi → False (bản ghi failed)
    assert not gw.send(mail(None))                                               # thiếu địa chỉ nhận
    _, data = _http.call("notify", "GET", "/v1/messages?to=an.nguyen")
    assert any(m["body"] == "Đơn đã xác nhận" for m in data["messages"])
    monkeypatch.setenv("ABC_FASHION_NOTIFY_URL", "http://127.0.0.1:9")
    assert not gw.send(mail("an.nguyen@gmail.com"))                              # dịch vụ tắt: không ném lỗi, không chặn nghiệp vụ


def test_auth_and_failure_injection(external):
    with pytest.raises(_http.GatewayUnavailable):
        os.environ["ABC_FASHION_PAYMENT_KEY"] = "sai-khoa"
        try:
            _http.call("payment", "GET", "/v1/transactions")
        finally:
            del os.environ["ABC_FASHION_PAYMENT_KEY"]
    _http.call("payment", "POST", "/__admin/behavior", {"fail_next": 1, "status": 503})
    with pytest.raises(_http.GatewayUnavailable):
        _http.call("payment", "GET", "/v1/transactions")
    assert _http.call("payment", "GET", "/v1/transactions")[0] == 200            # chỉ lỗi đúng một lần


# ---------------------------------------------------------------- đồng bộ vận chuyển nền (đơn tự tiến tới đã giao)
def test_shipment_sync_moves_order_to_delivered(db, http_mode, tk_root):
    from abc_fashion.control.dao.order_dao import OrderDAO
    from abc_fashion.control.dao.shipment_dao import ShipmentDAO
    from abc_fashion.model.sales import OrderStatus
    from abc_fashion.view._sync import ShipmentSync
    from abc_fashion.view.order.track_shipment_frm import TrackShipmentFrm

    db.execute("UPDATE \"tblOrder\" SET \"status\" = 'processing' WHERE \"id\" = 3")
    shipment = ShipmentDAO().get_shipment_by_order(Order(id=3))[0]
    shipment.to_address, shipment.from_location = "18 Hoàng Quốc Việt", "Kho TP.HCM"
    shipment.carrier, shipment.tracking_no = ShippingGateway().create_shipment(shipment)
    shipment.status = ShipmentStatus.PICKED_UP
    ShipmentDAO().update_shipment(shipment)
    assert OrderDAO().update_order_status(Order(id=3, status=OrderStatus.SHIPPED))

    track = TrackShipmentFrm(shipment)                                           # màn hình khách đang mở, tự nạp lại
    sync = ShipmentSync(tk_root, interval_ms=500)
    sync.start()
    deadline = time.time() + 40
    while time.time() < deadline and OrderDAO()._get_brief(3).status != OrderStatus.DELIVERED:
        tk_root.update()
        time.sleep(0.05)
    sync.stop()
    deadline = time.time() + 8                                                   # watch() kiểm tra mỗi 3 giây
    while time.time() < deadline and track.shipment.status != ShipmentStatus.DELIVERED:
        tk_root.update()
        time.sleep(0.05)
    assert track.shipment.status == ShipmentStatus.DELIVERED and len(track.tbl_shipment_event.get_children()) >= 3
    track.destroy()
    tk_root.update()
    assert OrderDAO()._get_brief(3).status == OrderStatus.DELIVERED
    statuses = [e.status for e in ShipmentDAO().get_shipment_event(shipment)]
    assert statuses[-3:] == [ShipmentStatus.PICKED_UP, ShipmentStatus.IN_TRANSIT, ShipmentStatus.DELIVERED]
    assert db.execute('SELECT "status" FROM "tblShipment" WHERE "id" = %s', (shipment.id,)).fetchone()["status"] == "delivered"
    _, data = _http.call("notify", "GET", "/v1/messages?event_type=order_delivered&to=an.nguyen")
    assert any("ORD-261020-001" in m["body"] for m in data["messages"])         # khách nhận thư "đã giao" qua dịch vụ e-mail
    assert db.execute('SELECT count(*) AS n FROM "tblNotification" WHERE "event_type" = \'order_delivered\' AND "status" = \'sent\'').fetchone()["n"] >= 2


# ---------------------------------------------------------------- trình quản lý dịch vụ nền
def test_manage_status_lists_running_services(external):
    out = subprocess.run([sys.executable, os.path.join(EXTERNAL, "manage.py"), "status"], capture_output=True,
                         timeout=60, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    lines = out.stdout.decode("utf-8").splitlines()
    assert out.returncode == 0
    for name in ("payment", "shipping", "notify"):
        assert any(line.startswith(name) and "đang chạy" in line for line in lines), lines
