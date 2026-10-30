"""Các trang của web khách hàng. Mỗi hàm: đọc request → gọi controller (abc_fashion.controller) → render / chuyển trang.

Không có nghiệp vụ ở đây: kiểm tra dữ liệu, quyền với đơn hàng (NFR03), tính tiền, giữ hàng, thanh toán… đều nằm
trong controller. Lỗi nghiệp vụ (BusinessError) được `app.py` đổi thành thông báo và quay lại trang trước.
"""
from __future__ import annotations

import functools
import time

from flask import (Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory,
                   session, url_for)

from abc_fashion.controller._errors import BusinessError, ServiceUnavailable
from abc_fashion.controller.auth_controller import AuthController
from abc_fashion.controller.cart_controller import CartController
from abc_fashion.controller.catalogue_controller import COLOURS, SIZES, SORTS, CatalogueController
from abc_fashion.controller.checkout_controller import CheckoutController
from abc_fashion.controller.order_controller import OrderController
from abc_fashion.controller.profile_controller import ProfileController
from abc_fashion.controller.return_controller import ReturnController
from abc_fashion.controller.review_controller import ReviewController
from abc_fashion.model.catalogue import FitType, Style
from abc_fashion.model.customer_data import LinkedMethodType, Address
from abc_fashion.model.fulfilment import Shipment
from abc_fashion.model.inventory import availability_text
from abc_fashion.model.returns import Resolution, ReturnReason, ReturnType, ReturnRequest
from abc_fashion.model.review import FitVote, ReviewStatus
from abc_fashion.model.sales import DeliveryService, OrderStatus, PaymentMethodType, Order
from abc_fashion.model.user import Customer

shop = Blueprint("shop", __name__)

_SESSION_FIELDS = ("id", "userId", "email", "full_name", "phone", "marketing_consent", "preferred_colours")


# ====================================================================== phiên đăng nhập
def current_customer() -> Customer | None:
    data = session.get("customer")
    return Customer(**data) if data else None


def _remember(customer: Customer) -> None:
    session["customer"] = {k: getattr(customer, k) for k in _SESSION_FIELDS}


def login_required(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if current_customer() is None:
            flash("Vui lòng đăng nhập để tiếp tục.", "warn")
            return redirect(url_for("shop.login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapper


@shop.app_context_processor
def _globals():
    customer = current_customer()
    count = 0
    if customer is not None:
        count = sum(i.quantity for i in CartController().get_cart(customer).items)
    return {"customer": customer, "cart_count": count, "categories_nav": CatalogueController().get_categories()}


def _int(value, default=0) -> int:
    try:
        return int(str(value).replace(".", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def _enum(cls, value):
    try:
        return cls(value) if value else None
    except ValueError:
        return None


# ====================================================================== media
@shop.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(current_app.config["MEDIA_DIR"], filename)


# ====================================================================== tài khoản (UC01, UC02)
@shop.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            actor = AuthController().login(request.form.get("email", ""), request.form.get("password", ""))
        except BusinessError as e:
            flash(str(e), "error")
            return render_template("login.html", email=request.form.get("email", ""))
        if not isinstance(actor, Customer):
            flash("Trang web chỉ dành cho khách hàng. Nhân viên và nhà cung cấp dùng ứng dụng desktop.", "error")
            return render_template("login.html", email=request.form.get("email", ""))
        session.clear()
        _remember(actor)
        flash(f"Xin chào {actor.full_name}!", "ok")
        nxt = request.args.get("next") or ""
        return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else url_for("shop.home"))
    return render_template("login.html", email="")


@shop.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("shop.home"))


@shop.route("/register", methods=["GET", "POST"])
def register():
    form = request.form
    if request.method == "POST":
        customer = Customer(email=form.get("email", ""), password=form.get("password", ""),
                            full_name=form.get("full_name", ""), phone=form.get("phone", ""),
                            marketing_consent=bool(form.get("marketing_consent")))
        try:
            AuthController().register(customer, form.get("confirm_password", ""))
        except BusinessError as e:
            flash(str(e), "error")
            return render_template("register.html", form=form)
        flash("Đăng ký thành công. Mời bạn đăng nhập.", "ok")
        return render_template("login.html", email=customer.email)
    return render_template("register.html", form={})


# ====================================================================== danh mục, tìm kiếm (UC04, UC05)
def _style_grid(styles: list[Style], catalogue: CatalogueController) -> list[Style]:
    images = catalogue.get_cover_images(styles)
    for s in styles:
        s.cover = images.get(s.id)
    return styles


@shop.route("/")
def home():
    catalogue = CatalogueController()
    styles = catalogue.browse_style(None, "", "", None, 0, 0, "newest")
    return render_template("home.html", styles=_style_grid(styles[:8], catalogue))


@shop.route("/catalogue")
def catalogue():
    ctl = CatalogueController()
    categories = ctl.get_categories()
    args = request.args
    category = next((c for c in categories if str(c.id) == args.get("category")), None)
    try:
        styles = ctl.browse_style(category, args.get("size", ""), args.get("colour", ""),
                                  _enum(FitType, args.get("fit")), _int(args.get("min")), _int(args.get("max")),
                                  args.get("sort") or "name")
    except BusinessError as e:
        flash(str(e), "error")
        styles = []
    return render_template("catalogue.html", styles=_style_grid(styles, ctl), categories=categories,
                           category=category, args=args, sizes=SIZES, colours=COLOURS, sorts=SORTS,
                           fit_types=list(FitType))


@shop.route("/search")
def search():
    ctl = CatalogueController()
    key = request.args.get("q", "").strip()
    styles = []
    if key:
        styles = ctl.search_style(key)
        if not styles:
            flash(f"Không tìm thấy \"{key}\". Hãy thử từ khoá khác, ví dụ: áo, váy, jeans.", "warn")
    return render_template("search.html", styles=_style_grid(styles, ctl), q=key, how="chữ")


@shop.route("/search/<how>", methods=["POST"])
def search_by_file(how):
    """Tìm bằng ảnh / file ghi âm (UC05). Dịch vụ AI lỗi → gợi ý tìm bằng chữ."""
    if how not in ("image", "voice"):
        abort(404)
    upload = request.files.get("file")
    if upload is None or not upload.filename:
        flash("Chọn một file", "error")
        return redirect(url_for("shop.search"))
    ctl, what = CatalogueController(), "ảnh" if how == "image" else "giọng nói"
    data = upload.read()
    try:
        ids = ctl.find_style_ids_by_image(data) if how == "image" else ctl.find_style_ids_by_voice(data)
    except Exception as e:                                    # noqa: BLE001 - AI tắt / file không đọc được
        flash(f"Tìm bằng {what} tạm thời không dùng được ({e}). Hãy tìm bằng chữ.", "warn")
        return redirect(url_for("shop.search"))
    styles = ctl.get_active_styles(ids)
    if not styles:
        flash(f"Không tìm thấy sản phẩm phù hợp với {what}. Hãy tìm bằng chữ.", "warn")
    return render_template("search.html", styles=_style_grid(styles, ctl), q="", how=what)


# ====================================================================== chi tiết sản phẩm, trợ lý AI (UC06, UC32, UC33)
@shop.route("/style/<int:style_id>")
def style_detail(style_id):
    ctl, customer = CatalogueController(), current_customer()
    style = ctl.get_style_detail(Style(id=style_id))
    if style.name is None or style.status is None:
        abort(404)
    offers = []
    for v in style.variants:
        level = ctl.get_stock_level(v)
        offers.append({"variant": v, "price": ctl.get_final_price(style, v), "available": level.available if level else 0,
                       "text": availability_text(level)})
    measures = sorted({e.measure for e in style.size_chart}, key=lambda m: list(type(m)).index(m))
    size_rows: dict[str, dict] = {}
    for e in style.size_chart:
        size_rows.setdefault(e.size_label, {})[e.measure] = e.value_cm
    if customer is not None:
        turns = [(t.question, t.answer) for t in ctl.get_assistant_history(customer, style)]
    else:
        turns = session.get("assistant", {}).get(str(style_id), [])
    return render_template("style.html", style=style, offers=offers, promotion=ctl.auto_promotion(style),
                           any_promotion=style.promotion, summary=ctl.summarise_reviews(style),
                           measures=measures, size_rows=size_rows, turns=turns,
                           images=[m for m in style.images if m.url and "://" not in m.url])


@shop.route("/style/<int:style_id>/ask", methods=["POST"])
def ask_assistant(style_id):
    question = request.form.get("question", "").strip()
    if question:
        ctl, customer = CatalogueController(), current_customer()
        style = ctl.get_style_detail(Style(id=style_id))
        started = time.perf_counter()
        try:
            result = ctl.ask_assistant(question, style)
        except Exception:                                     # noqa: BLE001 - trợ lý lỗi không chặn trang
            flash("Xin lỗi, trợ lý đang gặp sự cố. Bạn thử lại sau nhé.", "warn")
            return redirect(url_for("shop.style_detail", style_id=style_id, _anchor="assistant"))
        ctl.save_assistant_turn(customer, style, result, int((time.perf_counter() - started) * 1000))
        if customer is None:                                  # khách vãng lai: giữ hội thoại trong phiên
            history = session.get("assistant", {})
            history[str(style_id)] = (history.get(str(style_id), []) + [(result["question"], result["answer"])])[-10:]
            session["assistant"] = history
    return redirect(url_for("shop.style_detail", style_id=style_id, _anchor="assistant"))


# ====================================================================== giỏ hàng (UC07, UC29)
@shop.route("/cart/add", methods=["POST"])
@login_required
def cart_add():
    style = CatalogueController().get_style_detail(Style(id=_int(request.form.get("style_id"))))
    variant = next((v for v in style.variants if str(v.id) == request.form.get("variant_id")), None)
    qty = _int(request.form.get("quantity"), 1)
    CartController().add_to_cart(current_customer(), variant, qty)
    flash(f"Đã thêm {qty} × {variant.sku} vào giỏ", "ok")
    return redirect(url_for("shop.style_detail", style_id=style.id))


@shop.route("/cart")
@login_required
def cart():
    return render_template("cart.html", cart=CartController().get_cart(current_customer()),
                           short=session.pop("short", {}))


def _cart_item(ctl: CartController, item_id):
    item = next((i for i in ctl.get_cart(current_customer()).items if str(i.id) == str(item_id)), None)
    if item is None:
        raise BusinessError("Dòng hàng không còn trong giỏ")
    return item


@shop.route("/cart/<int:item_id>/update", methods=["POST"])
@login_required
def cart_update(item_id):
    ctl = CartController()
    ctl.update_quantity(_cart_item(ctl, item_id), _int(request.form.get("quantity"), -1))
    return redirect(url_for("shop.cart"))


@shop.route("/cart/<int:item_id>/remove", methods=["POST"])
@login_required
def cart_remove(item_id):
    ctl = CartController()
    ctl.remove_item(_cart_item(ctl, item_id))
    return redirect(url_for("shop.cart"))


@shop.route("/cart/checkout", methods=["POST"])
@login_required
def cart_checkout():
    ctl = CartController()
    short = ctl.check_availability(ctl.get_cart(current_customer()))
    if short:
        session["short"] = {str(i.id): getattr(i, "available", 0) for i in short}
        flash("Không đủ hàng: " + ", ".join(f"{i.sku} (còn {getattr(i, 'available', 0)})" for i in short), "error")
        return redirect(url_for("shop.cart"))
    return redirect(url_for("shop.checkout"))


# ====================================================================== thanh toán (UC08, UC26, UC28–UC31)
@shop.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    customer, ctl = current_customer(), CheckoutController()
    cart = CartController().get_cart(customer)
    if not cart.items:
        flash("Giỏ hàng trống", "warn")
        return redirect(url_for("shop.cart"))
    form = request.form if request.method == "POST" else request.args
    order = ctl.start_checkout(customer, cart)
    order.delivery_service = _enum(DeliveryService, form.get("delivery")) or DeliveryService.STANDARD
    codes = [c for c in form.get("vouchers", "").split(",") if c]
    for code in codes:                                        # áp lại các mã đã áp ở lần gửi trước
        try:
            ctl.apply_voucher(order, code)
        except BusinessError as e:
            flash(f"Mã {code}: {e}", "warn")
    ctl.recalc(order)
    action = form.get("action")
    addresses = ctl.get_addresses(customer)
    address = next((a for a in addresses if str(a.id) == form.get("address_id")),
                   next((a for a in addresses if a.is_default), addresses[0] if addresses else None))
    method_type = _enum(PaymentMethodType, form.get("method_type")) or PaymentMethodType.COD
    options = {t: ctl.get_payment_options(customer, t) for t in (PaymentMethodType.CARD, PaymentMethodType.E_WALLET)}
    method = next((m for m in options.get(method_type, []) if m and str(m.id) == form.get("method_id")), None)
    if request.method == "POST" and action == "voucher":
        try:
            v = ctl.apply_voucher(order, form.get("voucher_code", ""))
            flash(f"Đã áp dụng mã {v.code}", "ok")
        except BusinessError as e:
            flash(str(e), "error")
    elif request.method == "POST" and action == "place":
        try:
            ctl.place_order(customer, order, address, method_type, method, form.get("note", ""))
        except ServiceUnavailable as e:                       # đơn đã giữ hàng → trang kết quả để thanh toán lại
            flash(f"Cổng thanh toán tạm thời không phản hồi ({e}). Đơn đã được giữ, hãy bấm thanh toán lại.", "warn")
            return redirect(url_for("shop.order_result", order_id=order.id))
        except BusinessError as e:
            if order.id is None:
                flash(str(e), "error")
                return render_template("checkout.html", order=order, addresses=addresses, address=address,
                                       method_type=method_type, method=method, options=options, form=form)
            raise
        return redirect(url_for("shop.order_result", order_id=order.id))
    return render_template("checkout.html", order=order, addresses=addresses, address=address, method_type=method_type,
                           method=method, options=options, form=form)


@shop.route("/orders/<int:order_id>/result")
@login_required
def order_result(order_id):
    customer, ctl = current_customer(), CheckoutController()
    order = ctl.get_order(customer, Order(id=order_id))
    return render_template("order_result.html", order=order, retry=ctl.get_retry_options(customer),
                           pending=order.status == OrderStatus.PENDING_PAYMENT)


@shop.route("/orders/<int:order_id>/pay", methods=["POST"])
@login_required
def order_pay(order_id):
    customer, ctl = current_customer(), CheckoutController()
    order = ctl.get_order(customer, Order(id=order_id))
    choice = request.form.get("method", "")
    option = next(((t, m) for t, m in ctl.get_retry_options(customer)
                   if f"{t.value}:{m.id if m else ''}" == choice), None)
    if option is None:
        raise BusinessError("Chọn phương thức thanh toán")
    if not ctl.retry_payment(customer, order, *option):
        flash("Thanh toán thất bại. Hàng vẫn được giữ — hãy thử phương thức khác.", "error")
    return redirect(url_for("shop.order_result", order_id=order_id))


# ====================================================================== đơn hàng (UC09–UC12)
@shop.route("/orders")
@login_required
def orders():
    status = _enum(OrderStatus, request.args.get("status"))
    return render_template("orders.html", orders=OrderController().get_orders(current_customer(), status),
                           status=status, statuses=list(OrderStatus))


def _order(order_id) -> Order:
    return OrderController().get_order_detail(current_customer(), Order(id=order_id))


@shop.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    return render_template("order.html", order=_order(order_id), reasons=CANCEL_REASONS)


CANCEL_REASONS = ["Đổi ý, không muốn mua nữa", "Muốn đổi sản phẩm / cỡ khác", "Tìm được giá tốt hơn",
                  "Đặt nhầm địa chỉ", "Giao hàng quá lâu"]


@shop.route("/orders/<int:order_id>/cancel", methods=["POST"])
@login_required
def order_cancel(order_id):
    order = _order(order_id)
    reason = request.form.get("reason_detail", "").strip() or request.form.get("reason", "")
    message, warning = OrderController().cancel_order(order, reason)
    if warning:
        flash(warning, "warn")
    flash(message, "ok")
    return redirect(url_for("shop.order_detail", order_id=order_id))


@shop.route("/orders/<int:order_id>/received", methods=["POST"])
@login_required
def order_received(order_id):
    OrderController().confirm_received(_order(order_id))
    flash("Cảm ơn bạn đã xác nhận nhận hàng.", "ok")
    return redirect(url_for("shop.order_detail", order_id=order_id))


@shop.route("/orders/<int:order_id>/shipments/<int:shipment_id>", methods=["GET", "POST"])
@login_required
def track_shipment(order_id, shipment_id):
    order, ctl = _order(order_id), OrderController()
    shipment = next((s for s in order.shipments if s.id == shipment_id), None)
    if shipment is None:
        abort(404)
    if request.method == "POST":
        if not ctl.refresh_tracking(shipment):
            flash("Chưa có cập nhật mới", "warn")
        return redirect(url_for("shop.track_shipment", order_id=order_id, shipment_id=shipment_id))
    shipment = ctl.get_shipment(Shipment(id=shipment_id, orderId=order_id))
    return render_template("track.html", order=order, shipment=shipment, events=ctl.get_shipment_events(shipment))


# ====================================================================== đánh giá (UC13, UC34)
@shop.route("/orders/<int:order_id>/review/<int:item_id>", methods=["GET", "POST"])
@login_required
def review(order_id, item_id):
    order = _order(order_id)
    item = next((i for i in order.items if i.id == item_id), None)
    if item is None:
        abort(404)
    if request.method == "POST":
        f = request.form
        try:
            r = ReviewController().submit_review(item, _int(f.get("rating")), f.get("body", ""),
                                                 f.get("size_purchased", ""), _enum(FitVote, f.get("fit_vote")))
        except BusinessError as e:
            flash(str(e), "error")
            return render_template("review.html", order=order, item=item, form=f, fit_votes=list(FitVote))
        flash("Cảm ơn bạn! Đánh giá đã được đăng." if r.status == ReviewStatus.APPROVED
              else f"Đánh giá đang chờ duyệt ({r.moderation_note}).", "ok")
        return redirect(url_for("shop.order_detail", order_id=order_id))
    if not item.can_review:
        flash("Dòng hàng này chưa thể đánh giá hoặc đã được đánh giá.", "warn")
        return redirect(url_for("shop.order_detail", order_id=order_id))
    return render_template("review.html", order=order, item=item, form={"size_purchased": item.size_label},
                           fit_votes=list(FitVote))


# ====================================================================== trả / đổi hàng (UC14)
@shop.route("/orders/<int:order_id>/return", methods=["GET", "POST"])
@login_required
def return_request(order_id):
    order, ctl = _order(order_id), ReturnController()
    if not order.can_return:
        flash("Đơn này không còn trong hạn trả / đổi hàng hoặc đã có yêu cầu.", "warn")
        return redirect(url_for("shop.order_detail", order_id=order_id))
    replacements = {i.id: ctl.get_replacement_options(i) for i in order.items}
    form = request.form
    if request.method == "POST":
        return_type = _enum(ReturnType, form.get("return_type")) or ReturnType.RETURN
        try:
            items = []
            for i in order.items:
                qty = _int(form.get(f"qty_{i.id}"))
                if qty > 0:
                    rep = next((v for v in replacements[i.id] if str(v.id) == form.get(f"rep_{i.id}")), None)
                    items.append(ctl.make_return_item(i, qty, return_type, rep))
            evidence = [ctl.store_evidence(f.filename, f.read()) for f in request.files.getlist("evidence")
                        if f and f.filename]
            rr = ReturnRequest(orderId=order.id, return_type=return_type,
                               desired_resolution=Resolution.EXCHANGE if return_type == ReturnType.EXCHANGE
                               else Resolution.REFUND,
                               reason_code=_enum(ReturnReason, form.get("reason_code")),
                               reason_detail=form.get("reason_detail", ""))
            rr.items = items
            ctl.submit_return_request(current_customer(), order, rr, evidence)
        except BusinessError as e:
            flash(str(e), "error")
            return render_template("return.html", order=order, replacements=replacements, form=form,
                                   reasons=list(ReturnReason), types=list(ReturnType))
        flash(f"Đã gửi yêu cầu {rr.return_no}. Bộ phận chăm sóc khách hàng sẽ phản hồi sớm.", "ok")
        return redirect(url_for("shop.order_detail", order_id=order_id))
    return render_template("return.html", order=order, replacements=replacements, form={},
                           reasons=list(ReturnReason), types=list(ReturnType))


# ====================================================================== hồ sơ (UC03)
@shop.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    customer, ctl = current_customer(), ProfileController()
    if request.method == "POST":
        f = request.form
        ctl.update_profile(customer, f.get("full_name", ""), f.get("phone", ""),
                           f.get("preferred_colours", "").split(","), bool(f.get("marketing_consent")))
        _remember(customer)
        flash("Đã lưu thông tin", "ok")
        return redirect(url_for("shop.profile"))
    return render_template("profile.html", addresses=ctl.get_addresses(customer),
                           methods=ctl.get_payment_methods(customer), sizes=ctl.get_saved_sizes(customer),
                           categories=ctl.get_categories(), providers={t: ctl.get_providers(t) for t in LinkedMethodType},
                           method_types=list(LinkedMethodType))


@shop.route("/profile/address/new", methods=["GET", "POST"], defaults={"address_id": None})
@shop.route("/profile/address/<int:address_id>", methods=["GET", "POST"])
@login_required
def address(address_id):
    customer, ctl = current_customer(), ProfileController()
    current = None
    if address_id is not None:
        current = next((a for a in ctl.get_addresses(customer) if a.id == address_id), None)
        if current is None:
            abort(404)
    back = request.values.get("back") or url_for("shop.profile")
    if request.method == "POST":
        f = request.form
        a = Address(id=address_id, recipient_name=f.get("recipient_name"), phone=f.get("phone"), street=f.get("street"),
                    ward=f.get("ward"), district=f.get("district"), city=f.get("city"),
                    is_default=bool(f.get("is_default")))
        try:
            ctl.save_address(customer, a)
        except BusinessError as e:
            flash(str(e), "error")
            return render_template("address.html", address=a, back=back)
        flash("Đã lưu địa chỉ", "ok")
        return redirect(back if back.startswith("/") and not back.startswith("//") else url_for("shop.profile"))
    return render_template("address.html", back=back,
                           address=current or Address(recipient_name=customer.full_name, phone=customer.phone))


@shop.route("/profile/address/<int:address_id>/delete", methods=["POST"])
@login_required
def address_delete(address_id):
    ctl = ProfileController()
    a = next((a for a in ctl.get_addresses(current_customer()) if a.id == address_id), None)
    if a is None:
        abort(404)
    ctl.delete_address(a)
    flash("Đã xoá địa chỉ", "ok")
    return redirect(url_for("shop.profile"))


@shop.route("/profile/payment", methods=["POST"])
@login_required
def payment_link():
    method = ProfileController().link_payment_method(current_customer(),
                                                     _enum(LinkedMethodType, request.form.get("method_type")),
                                                     request.form.get("provider", ""),
                                                     bool(request.form.get("is_default")))
    flash(f"Đã liên kết {method.provider} {method.masked_number}", "ok")
    return redirect(url_for("shop.profile"))


@shop.route("/profile/payment/<int:method_id>/remove", methods=["POST"])
@login_required
def payment_remove(method_id):
    ctl = ProfileController()
    m = next((m for m in ctl.get_payment_methods(current_customer()) if m.id == method_id), None)
    if m is None:
        abort(404)
    ctl.remove_payment_method(m)
    flash("Đã gỡ liên kết", "ok")
    return redirect(url_for("shop.profile"))


@shop.route("/profile/size", methods=["POST"])
@login_required
def size_save():
    ctl = ProfileController()
    category = next((c for c in ctl.get_categories() if str(c.id) == request.form.get("category_id")), None)
    ctl.save_size(current_customer(), category, request.form.get("size_label", ""))
    flash("Đã lưu cỡ", "ok")
    return redirect(url_for("shop.profile"))
