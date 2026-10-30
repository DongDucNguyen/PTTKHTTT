"""ConfirmOrderFrm — Kết quả đặt hàng; thanh toán lại khi lần trước thất bại."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.checkout_controller import CheckoutController
from abc_fashion.model.sales import OrderStatus, PaymentKind, PaymentMethodType, PaymentStatus, Order
from abc_fashion.model.user import Customer
from abc_fashion.view._util import ChoiceBox, body, fill_table, guarded, label, make_table, money, ship_text, show
from abc_fashion.view.order.order_detail_frm import OrderDetailFrm


class ConfirmOrderFrm(tk.Toplevel):
    def __init__(self, customer: Customer, order: Order):
        super().__init__()
        self.customer = customer
        self.checkout_controller = CheckoutController()
        self.order = order
        self._build()
        self._reload()

    def _build(self) -> None:
        f = body(self, "Kết quả đặt hàng")
        self.lbl_order_no = ttk.Label(f, style="H2.TLabel")
        self.lbl_order_no.grid(row=0, column=0, columnspan=3, sticky="w")
        self.lbl_status = ttk.Label(f)
        self.lbl_status.grid(row=1, column=0, columnspan=3, sticky="w")
        self.tbl_order_item = make_table(f, [("sku", "SKU", 100), ("name", "Sản phẩm", 200), ("qty", "SL", 40),
                                             ("total", "Thành tiền", 100)], height=5)
        self.tbl_order_item.box.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=6)
        self.tbl_shipment = make_table(f, [("id", "Kiện", 60), ("loc", "Kho", 140), ("items", "Hàng", 280),
                                           ("status", "Trạng thái", 110)], height=3)
        self.tbl_shipment.box.grid(row=3, column=0, columnspan=3, sticky="nsew")
        self.lbl_grand_total = ttk.Label(f, style="H2.TLabel")
        self.lbl_grand_total.grid(row=4, column=0, columnspan=3, sticky="e", pady=4)
        self.lbl_payment_result = ttk.Label(f, wraplength=560)
        self.lbl_payment_result.grid(row=5, column=0, columnspan=3, sticky="w")
        retry = ttk.Frame(f)
        retry.grid(row=6, column=0, columnspan=3, sticky="w", pady=4)
        self.cbo_method = ChoiceBox(retry, width=34)
        self.cbo_method.pack(side="left")
        self.btn_retry_payment = ttk.Button(retry, text="Thanh toán lại", command=self.on_retry_payment)
        self.btn_retry_payment.pack(side="left", padx=4)
        bar = ttk.Frame(f)
        bar.grid(row=7, column=0, columnspan=3, sticky="e", pady=(8, 0))
        self.btn_view_order = ttk.Button(bar, text="Xem đơn hàng", command=self.on_view_order)
        self.btn_view_order.pack(side="left", padx=4)
        self.btn_continue_shopping = ttk.Button(bar, text="Tiếp tục mua sắm", command=self.on_continue_shopping)
        self.btn_continue_shopping.pack(side="left")

    def _reload(self) -> None:
        self.order = self.checkout_controller.get_order(self.customer, self.order)
        o = self.order
        self.lbl_order_no.config(text=f"Đơn hàng {o.order_no}")
        self.lbl_status.config(text=f"Trạng thái: {label(o.status)}  ·  Giao tới: {ship_text(o)}")
        fill_table(self.tbl_order_item, [(i.id, (i.sku, i.style_name, i.quantity, money(i.line_total))) for i in o.items])
        fill_table(self.tbl_shipment, [(s.id, (s.id, getattr(s, "location_name", ""),
                                               ", ".join(f"{r.sku}×{r.quantity}" for r in s.records), label(s.status)))
                                       for s in o.shipments])
        self.lbl_grand_total.config(text=f"Tổng cộng: {money(o.grand_total)}")
        charges = [p for p in o.payments if p.kind == PaymentKind.CHARGE]
        last = charges[-1] if charges else None
        pending = o.status == OrderStatus.PENDING_PAYMENT
        if last is None:
            text = "Chưa thanh toán."
        elif last.method == PaymentMethodType.COD:
            text = "Thanh toán khi nhận hàng (COD)."
        elif last.status == PaymentStatus.SUCCEEDED:
            text = f"Thanh toán thành công, mã giao dịch {last.transaction_ref}."
        else:
            text = "Thanh toán thất bại. Hàng vẫn được giữ cho bạn — hãy thanh toán lại hoặc chọn phương thức khác."
        show(self.lbl_payment_result, text, ok=not pending)
        self.cbo_method.set_choices([(f"{label(t)} {m.provider} {m.masked_number}" if m else label(t), (t, m))
                                     for t, m in self.checkout_controller.get_retry_options(self.customer)])
        for w in (self.cbo_method, self.btn_retry_payment):
            w.state(["!disabled"] if pending else ["disabled"])

    @guarded
    def on_retry_payment(self) -> None:
        if self.order.status != OrderStatus.PENDING_PAYMENT or self.cbo_method.value() is None:
            return
        mtype, method = self.cbo_method.value()
        self.checkout_controller.retry_payment(self.customer, self.order, mtype, method)
        self._reload()

    @guarded
    def on_view_order(self) -> None:
        OrderDetailFrm(self.customer, self.order)

    def on_continue_shopping(self) -> None:
        self.destroy()
