"""Kiểm thử giao diện trên CSDL thử: mở mọi màn hình, rồi chạy kịch bản trình diễn (mục 14.2) qua các handler.

Hộp thoại được thay bằng hàm giả; lỗi hiện bằng `messagebox.showerror` làm test thất bại.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog

import pytest

from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.model.catalogue import ProductVariant, Style
from abc_fashion.model.inventory import RestockRequest
from abc_fashion.model.returns import InspectionResult, ReturnStatus, ReturnRequest
from abc_fashion.model.sales import OrderStatus, PaymentMethodType, Order, Promotion
from abc_fashion.model.user import Customer, StaffMember, Supplier, User


@pytest.fixture()
def ui(db, tk_root, monkeypatch):
    errors: list[str] = []
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: errors.append(" | ".join(map(str, a))))
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showwarning", lambda *a, **k: errors.append("warn: " + " | ".join(map(str, a))))
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(simpledialog, "askinteger", lambda *a, **k: k.get("initialvalue"))
    monkeypatch.setattr(tk.Misc, "wait_window", lambda self, window=None: None)
    monkeypatch.setattr(tk.Misc, "wait_visibility", lambda self, window=None: None)
    root = tk_root
    root.errors = errors
    yield root
    for w in list(root.winfo_children()):
        w.destroy()
    assert not errors, errors


def newest(root, cls):
    wins = [w for w in root.winfo_children() if isinstance(w, cls)]
    assert wins, f"không thấy cửa sổ {cls.__name__}"
    return wins[-1]


def staff(db, role_user_id):
    from abc_fashion.control.dao.staff_member_dao import StaffMemberDAO
    return StaffMemberDAO().get_staff_member_by_user(User(id=role_user_id))


def test_every_screen_opens(ui, db):
    from abc_fashion.control.dao.customer_dao import CustomerDAO
    from abc_fashion.view.account import (admin_home_frm, audit_log_frm, customer_home_frm, edit_account_frm,
                                          edit_address_frm, link_payment_method_frm, login_frm, profile_frm,
                                          register_frm, search_account_frm)
    from abc_fashion.view.catalogue import assistant_frm, browse_style_frm, search_style_frm, style_detail_frm
    from abc_fashion.view.checkout import cart_frm, checkout_frm, confirm_order_frm
    from abc_fashion.view.inventory import (adjust_stock_frm, confirm_restock_frm, edit_restock_request_frm,
                                            manage_restock_frm, select_variant_frm, stock_level_frm,
                                            stock_movement_frm, supplier_home_frm, warehouse_home_frm)
    from abc_fashion.view.order import (cancel_request_frm, order_detail_frm, order_list_frm, return_request_frm,
                                        review_frm, track_shipment_frm)
    from abc_fashion.view.order_admin import manage_order_frm, manager_home_frm, search_order_frm
    from abc_fashion.view.product import edit_style_frm, edit_variant_frm, manage_style_frm
    from abc_fashion.view.promotion import (edit_promotion_frm, manage_promotion_frm, merchandiser_home_frm,
                                            select_style_frm)
    from abc_fashion.view.report import (marketing_home_frm, return_detail_frm, return_report_frm, sales_detail_frm,
                                         sales_report_frm, select_report_frm)
    from abc_fashion.view.returns import (customer_service_home_frm, inspect_return_frm, process_return_frm,
                                          search_return_request_frm)
    from abc_fashion.view.review import manage_review_frm
    from abc_fashion.control.dao.style_stat_dao import StyleStatDAO
    from abc_fashion.control.dao.return_stat_dao import ReturnStatDAO
    from datetime import date

    c = CustomerDAO().get_customer_by_user(User(id=10))
    admin, mgr, merch, mkt, cs, wh = (staff(db, i) for i in (1, 2, 3, 4, 5, 6))
    sup = Supplier(id=2, name="Denim Việt", userId=9)
    order1 = OrderDAO().get_order_detail(Order(id=1))
    order3 = OrderDAO().get_order_detail(Order(id=3))
    level = StockLevelDAO().search_stock_level(None, "", False)[0]
    s1 = StyleStatDAO().get_style_stat(date(2026, 9, 1), date(2026, 10, 31), None, None)[0]
    r1 = ReturnStatDAO().get_return_stat(date(2026, 9, 1), date(2026, 10, 31), None)[0]
    opened = [
        login_frm.LoginFrm(), register_frm.RegisterFrm(), customer_home_frm.CustomerHomeFrm(c),
        admin_home_frm.AdminHomeFrm(admin), manager_home_frm.ManagerHomeFrm(mgr),
        merchandiser_home_frm.MerchandiserHomeFrm(merch), marketing_home_frm.MarketingHomeFrm(mkt),
        customer_service_home_frm.CustomerServiceHomeFrm(cs), warehouse_home_frm.WarehouseHomeFrm(wh),
        supplier_home_frm.SupplierHomeFrm(sup), profile_frm.ProfileFrm(c), edit_address_frm.EditAddressFrm(c, None),
        link_payment_method_frm.LinkPaymentMethodFrm(c), search_account_frm.SearchAccountFrm(admin),
        audit_log_frm.AuditLogFrm(admin), browse_style_frm.BrowseStyleFrm(None), search_style_frm.SearchStyleFrm(c, "áo"),
        style_detail_frm.StyleDetailFrm(c, Style(id=2)), cart_frm.CartFrm(c),
        confirm_order_frm.ConfirmOrderFrm(c, Order(id=3)), order_list_frm.OrderListFrm(c),
        order_detail_frm.OrderDetailFrm(c, order1), cancel_request_frm.CancelRequestFrm(order3),
        review_frm.ReviewFrm(c, order1.items[0]), track_shipment_frm.TrackShipmentFrm(order1.shipments[0]),
        search_order_frm.SearchOrderFrm(mgr), manage_order_frm.ManageOrderFrm(mgr, order3),
        manage_style_frm.ManageStyleFrm(admin), edit_style_frm.EditStyleFrm(admin, Style(id=1)),
        edit_style_frm.EditStyleFrm(admin, None), edit_variant_frm.EditVariantFrm(admin, Style(id=1, code="ST-W001"), None),
        manage_promotion_frm.ManagePromotionFrm(merch), edit_promotion_frm.EditPromotionFrm(merch, Promotion(id=1)),
        edit_promotion_frm.EditPromotionFrm(merch, None), select_style_frm.SelectStyleFrm([]),
        select_report_frm.SelectReportFrm(mkt), sales_report_frm.SalesReportFrm(mkt),
        sales_detail_frm.SalesDetailFrm(s1, date(2026, 9, 1), date(2026, 10, 31)), return_report_frm.ReturnReportFrm(mkt),
        return_detail_frm.ReturnDetailFrm(r1, date(2026, 9, 1), date(2026, 10, 31)),
        search_return_request_frm.SearchReturnRequestFrm(cs), search_return_request_frm.SearchReturnRequestFrm(wh),
        process_return_frm.ProcessReturnFrm(cs, ReturnRequest(id=1)),
        inspect_return_frm.InspectReturnFrm(wh, ReturnRequest(id=1)), manage_review_frm.ManageReviewFrm(cs),
        stock_level_frm.StockLevelFrm(wh), adjust_stock_frm.AdjustStockFrm(wh, level),
        stock_movement_frm.StockMovementFrm(ProductVariant(id=1, sku="W001-WHT-S")),
        manage_restock_frm.ManageRestockFrm(wh), edit_restock_request_frm.EditRestockRequestFrm(wh, None),
        edit_restock_request_frm.EditRestockRequestFrm(wh, RestockRequest(id=2)),
        select_variant_frm.SelectVariantFrm(), confirm_restock_frm.ConfirmRestockFrm(sup, RestockRequest(id=1)),
    ]
    detail = newest(ui, style_detail_frm.StyleDetailFrm)
    opened += [assistant_frm.AssistantFrm(c, detail.style),
               checkout_frm.CheckoutFrm(c, newest(ui, cart_frm.CartFrm).cart),
               edit_account_frm.EditAccountFrm(admin, search_account_frm.SearchAccountFrm(admin).list_user[0])]
    rr_order = OrderDAO().get_order_detail(Order(id=2))
    opened.append(return_request_frm.ReturnRequestFrm(CustomerDAO().get_customer_by_user(User(id=11)), rr_order))
    ui.update()
    assert len({type(w).__name__ for w in opened}) == 53


def test_demo_scenario_end_to_end(ui, db):
    """Mục 14.2: thêm 2 biến thể ở 2 kho → voucher → thẻ bị từ chối → thanh toán lại → giao 2 kiện →
    nhận hàng → đánh giá → trả 1 món → duyệt, lấy hàng → kiểm tra đạt → hoàn tiền → báo cáo."""
    from abc_fashion.view.account.login_frm import LoginFrm
    from abc_fashion.view.account.customer_home_frm import CustomerHomeFrm
    from abc_fashion.view.catalogue.style_detail_frm import StyleDetailFrm
    from abc_fashion.view.checkout.cart_frm import CartFrm
    from abc_fashion.view.checkout.checkout_frm import CheckoutFrm
    from abc_fashion.view.checkout.confirm_order_frm import ConfirmOrderFrm
    from abc_fashion.view.order.order_detail_frm import OrderDetailFrm
    from abc_fashion.view.order.return_request_frm import ReturnRequestFrm
    from abc_fashion.view.order.review_frm import ReviewFrm
    from abc_fashion.view.order_admin.manage_order_frm import ManageOrderFrm
    from abc_fashion.view.returns.inspect_return_frm import InspectReturnFrm
    from abc_fashion.view.returns.process_return_frm import ProcessReturnFrm

    login = LoginFrm()
    login.txt_email.insert(0, "an.nguyen@gmail.com")
    login.txt_password.insert(0, "abc12345")
    login.on_login()
    customer = newest(ui, CustomerHomeFrm).customer

    for style_id, colour, size in ((1, "Trắng", "M"), (2, "Đỏ", "M")):         # kho Hà Nội + kho TP.HCM
        d = StyleDetailFrm(customer, Style(id=style_id))
        d.cbo_colour.set(colour)
        d._on_colour()
        d.cbo_size.set(size)
        d.on_select_variant()
        d.spn_quantity.set(1)
        d.on_add_to_cart()

    cart = CartFrm(customer)
    assert len(cart.cart.items) == 2
    cart.on_checkout()
    co = newest(ui, CheckoutFrm)
    co.txt_voucher_code.insert(0, "xuanhe10")
    co.on_apply_voucher()
    assert co.order.discount == (450_000 + 690_000) // 10
    co.var_payment_method.set(PaymentMethodType.CARD.value)
    co._on_change_payment_method()
    declined = next(i for i, v in enumerate(co.cbo_linked_method._values) if v.masked_number.endswith("0002"))
    co.cbo_linked_method.current(declined)
    co.on_place_order()
    conf = newest(ui, ConfirmOrderFrm)
    order = conf.order
    assert order.status == OrderStatus.PENDING_PAYMENT and len(order.shipments) == 2      # tách 2 kiện
    good = next(i for i, v in enumerate(conf.cbo_method._values) if v[1] and v[1].masked_number.endswith("4242"))
    conf.cbo_method.current(good)
    conf.on_retry_payment()
    assert conf.order.status == OrderStatus.CONFIRMED

    mgr = staff(db, 2)
    mo = ManageOrderFrm(mgr, order)
    for target in (OrderStatus.PROCESSING, OrderStatus.PARTIALLY_SHIPPED, OrderStatus.SHIPPED, OrderStatus.DELIVERED):
        mo.cbo_new_status.select_value(target)
        if target == OrderStatus.PARTIALLY_SHIPPED:
            mo.tbl_shipment.selection_set(str(mo.order.shipments[0].id))
        mo.on_update_status()
        assert mo.order.status == target, (target, mo.lbl_message.cget("text"))

    od = OrderDetailFrm(customer, order)
    od.on_confirm_received()
    assert od.order.status == OrderStatus.COMPLETED
    item = od.order.items[0]
    rv = ReviewFrm(customer, item)
    rv.txa_body.insert("1.0", "Vải mát, đúng mô tả")
    rv.on_submit()

    rr = ReturnRequestFrm(customer, od.order)
    rr.tbl_order_item.selection_set(str(item.id))
    rr.cbo_reason_code.current(1)                                   # quá rộng
    rr.on_select_item()
    rr.on_submit()
    request = ReturnRequestDAO().get_return_request_by_order(order)
    assert request.status == ReturnStatus.REQUESTED

    cs, wh = staff(db, 5), staff(db, 6)
    pr = ProcessReturnFrm(cs, request)
    pr.on_authorise()
    pr.on_create_pickup()
    assert pr.return_request.status == ReturnStatus.IN_TRANSIT
    ins = InspectReturnFrm(wh, request)
    ins.tbl_return_item.selection_set(str(ins.return_request.items[0].id))
    ins.cbo_inspection_result.select_value(InspectionResult.PASSED)
    ins.on_save_inspection()
    ins.on_finish()
    pr = ProcessReturnFrm(cs, request)
    pr.on_refund()
    pr.on_close()
    assert pr.return_request.status == ReturnStatus.CLOSED

    final = OrderDAO().get_order_detail(order)
    refunds = [p.amount for p in final.payments if p.kind.value == "refund"]
    unit, disc = final.items[0].unit_price, final.items[0].discount
    assert refunds == [unit - disc]                                   # hoàn đúng số sau giảm giá
    rows = db.execute('SELECT l."on_hand", coalesce(sum(m."quantity_change"),0) AS s FROM "tblStockLevel" l '
                      'LEFT JOIN "tblStockMovement" m ON m."productVariantId" = l."productVariantId" '
                      'GROUP BY l."id"').fetchall()
    assert all(r["on_hand"] == r["s"] for r in rows)                  # sổ kho khớp tồn
    # biến thể trả về đã nhập lại kho: W001-WHT-M bán 1 (seed) + 1 (kịch bản), trả 1
    assert db.execute('SELECT "on_hand" FROM "tblStockLevel" WHERE "productVariantId" = 2').fetchone()["on_hand"] == 15
