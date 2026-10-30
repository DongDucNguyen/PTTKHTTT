"""Ứng dụng web ABC Fashion dành cho khách hàng (Flask).

Theo MVC, web là một **view** khác của cùng hệ thống, song song với giao diện desktop tkinter:
- View      = `templates/*.html` (Jinja2) + `static/` — chỉ hiển thị, không gọi CSDL.
- Controller = các controller sẵn có trong `abc_fashion.controller` (dùng chung với desktop). `routes.py` chỉ là lớp
  vỏ HTTP mỏng: đọc request → gọi controller → chọn template / chuyển trang.
- Model     = `abc_fashion.model` (entity + quy tắc thuần), truy cập dữ liệu qua `abc_fashion.control` (DAO, gateway).
`check_gen.py` kiểm tra gói này chỉ import controller + model (không DAO, không psycopg, không tkinter).

Chạy:  cd code && ../.venv/Scripts/python.exe -m abc_fashion_web       (mặc định http://127.0.0.1:8000)
"""
from __future__ import annotations

import logging
import os
import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for

from abc_fashion.controller import _connection
from abc_fashion.controller._errors import AccessDenied, BusinessError, ServiceUnavailable
from abc_fashion.controller._media import MEDIA_DIR
from abc_fashion.view._format import fmt_dt, label, money, ship_text

log = logging.getLogger("abc_fashion")


def create_app(start_background: bool = True) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("ABC_FASHION_WEB_SECRET") or secrets.token_hex(32)
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024                     # ảnh / video bằng chứng
    app.config["MEDIA_DIR"] = MEDIA_DIR
    _connection.use_connection_per_thread()                                  # mỗi request một kết nối CSDL

    from abc_fashion_web.routes import shop
    app.register_blueprint(shop)

    app.add_template_filter(money, "money")
    app.add_template_filter(label, "label")
    app.add_template_filter(fmt_dt, "dt")
    app.add_template_filter(ship_text, "ship_text")

    @app.teardown_request
    def _close_connection(exc):
        _connection.release_connection()

    # ---------- CSRF: mọi form POST mang token của phiên ----------
    def csrf_token() -> str:
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_urlsafe(24)
        return session["_csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def _check_csrf():
        token = session.get("_csrf")
        if request.method == "POST" and (not token or request.form.get("_csrf") != token):
            flash("Phiên làm việc đã hết hạn, vui lòng thử lại.", "error")
            return redirect(request.referrer or url_for("shop.home"))

    # ---------- lỗi nghiệp vụ từ controller → thông báo cho khách ----------
    def back():
        return redirect(request.referrer or url_for("shop.home"))

    @app.errorhandler(AccessDenied)
    def _denied(e):
        return render_template("error.html", title="Không có quyền", message=str(e)), 403

    @app.errorhandler(BusinessError)
    def _business(e):
        flash(str(e), "error")
        return back()

    @app.errorhandler(ServiceUnavailable)
    def _service(e):
        flash(f"Dịch vụ bên ngoài tạm thời không phản hồi ({e}). Vui lòng thử lại sau.", "warn")
        return back()

    @app.errorhandler(404)
    def _not_found(e):
        return render_template("error.html", title="Không tìm thấy", message="Trang hoặc sản phẩm không tồn tại."), 404

    if start_background and _connection.external_services_enabled():
        from abc_fashion_web._background import start
        start()
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    port = int(os.environ.get("ABC_FASHION_WEB_PORT", "8000"))
    create_app().run(host=os.environ.get("ABC_FASHION_WEB_HOST", "127.0.0.1"), port=port, threaded=True)
