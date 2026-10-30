"""Ứng dụng web khách hàng (abc_fashion_web) trên CSDL thử: đăng ký → đăng nhập → duyệt → giỏ → thanh toán → đơn → huỷ;
kiểm tra quyền (NFR03) và chặn tài khoản nhân viên. Web chỉ gọi controller dùng chung với desktop.
"""
from __future__ import annotations

import re

import pytest

from abc_fashion.model.sales import OrderStatus


@pytest.fixture()
def client(db):
    from abc_fashion.control.dao.dao import DAO
    from abc_fashion_web.app import create_app

    app = create_app(start_background=False)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    DAO._release_thread_connection()
    DAO._per_thread = False                         # các test desktop sau dùng lại kết nối chung


def post(client, url, data=None, **kw):
    with client.session_transaction() as s:
        token = s.setdefault("_csrf", "test-token")
    return client.post(url, data={**(data or {}), "_csrf": token}, **kw)


def login(client, email, password="abc12345"):
    return post(client, "/login", {"email": email, "password": password})


def test_customer_journey(client, db):
    assert client.get("/").status_code == 200
    assert client.get("/catalogue").status_code == 200
    assert client.get("/search?q=áo").status_code == 200

    r = post(client, "/register", {"full_name": "Khách Web", "email": "web@example.com", "phone": "0912345678",
                                   "password": "matkhau123", "confirm_password": "matkhau123"})
    assert "Đăng ký thành công" in r.get_data(as_text=True)
    assert login(client, "web@example.com", "matkhau123").status_code == 302

    page = client.get("/style/1").get_data(as_text=True)
    variant = re.search(r'name="variant_id" value="(\d+)"[^>]*checked', page.replace("\n", " ")).group(1)
    post(client, "/cart/add", {"style_id": "1", "variant_id": variant, "quantity": "1"})
    assert "Tạm tính" in client.get("/cart").get_data(as_text=True)

    assert post(client, "/cart/checkout").headers["Location"].endswith("/checkout")
    r = post(client, "/profile/address/new", {"recipient_name": "Khách Web", "phone": "0912345678", "street": "1 Lê Lợi",
                                              "ward": "Bến Nghé", "district": "Quận 1", "city": "TP.HCM", "is_default": "1"})
    assert r.status_code == 302
    page = client.get("/checkout").get_data(as_text=True)
    address_id = re.search(r'name="address_id" value="(\d+)"', page).group(1)
    r = post(client, "/checkout", {"action": "place", "address_id": address_id, "delivery": "standard",
                                   "method_type": "cod", "note": "Giao giờ hành chính"})
    order_id = int(re.search(r"/orders/(\d+)/result", r.headers["Location"]).group(1))
    status = db.execute('SELECT "status" FROM "tblOrder" WHERE "id" = %s', (order_id,)).fetchone()["status"]
    assert status == OrderStatus.CONFIRMED.value
    assert "COD" in client.get(f"/orders/{order_id}/result").get_data(as_text=True)
    assert client.get("/orders").status_code == 200
    assert "Huỷ đơn" in client.get(f"/orders/{order_id}").get_data(as_text=True)

    post(client, f"/orders/{order_id}/cancel", {"reason": "Đổi ý, không muốn mua nữa"})
    status = db.execute('SELECT "status" FROM "tblOrder" WHERE "id" = %s', (order_id,)).fetchone()["status"]
    assert status == OrderStatus.CANCELLED.value
    assert client.get("/orders/1").status_code == 403                        # đơn của khách khác (NFR03)


def test_business_errors_become_messages(client, db):
    login(client, "an.nguyen@gmail.com")
    r = post(client, "/cart/add", {"style_id": "1", "variant_id": "", "quantity": "1"}, follow_redirects=True)
    assert "Chọn màu và cỡ" in r.get_data(as_text=True)


def test_staff_cannot_use_customer_site(client, db):
    r = login(client, "admin@abc.vn")
    assert r.status_code == 200 and "chỉ dành cho khách hàng" in r.get_data(as_text=True)
    assert client.get("/orders").status_code == 302                           # chưa đăng nhập → về trang đăng nhập


def test_post_without_csrf_token_is_rejected(client, db):
    r = client.post("/login", data={"email": "an.nguyen@gmail.com", "password": "abc12345"}, follow_redirects=True)
    assert "Phiên làm việc đã hết hạn" in r.get_data(as_text=True)
