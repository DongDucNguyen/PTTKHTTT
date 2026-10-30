"""CheckoutFrm — Thanh toán (UC08 + UC26, UC28–UC31)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller._errors import ServiceUnavailable
from abc_fashion.controller.checkout_controller import CheckoutController
from abc_fashion.model.customer_data import Address, PaymentMethod
from abc_fashion.model.sales import DeliveryService, PaymentMethodType, Cart, Voucher
from abc_fashion.model.user import Customer
from abc_fashion.view._util import (ChoiceBox, body, fill_table, guarded, label, make_table, message_label, modal,
                                    money, show, warn)
from abc_fashion.view.account.edit_address_frm import EditAddressFrm
from abc_fashion.view.checkout.confirm_order_frm import ConfirmOrderFrm


class CheckoutFrm(tk.Toplevel):
    def __init__(self, customer: Customer, cart: Cart):
        super().__init__()
        self.customer = customer
        self.cart = cart
        self.checkout_controller = CheckoutController()
        self.list_address: list[Address] = []
        self.list_payment_method: list[PaymentMethod] = []
        self.order_placed = False
        self._build()
        self._load_addresses()
        self.order = self.checkout_controller.start_checkout(customer, cart)
        self.list_voucher: list[Voucher] = self.order.vouchers
        self._on_change_payment_method()
        self._show_totals()

    def _build(self) -> None:
        f = body(self, "Thanh toán")
        self.tbl_order_item = make_table(f, [("sku", "SKU", 100), ("name", "Sản phẩm", 190), ("var", "Màu / cỡ", 80),
                                             ("qty", "SL", 40), ("price", "Đơn giá", 90), ("disc", "Giảm", 80),
                                             ("total", "Thành tiền", 100)], height=6)
        self.tbl_order_item.box.grid(row=0, column=0, columnspan=2, sticky="nsew")

        left = ttk.LabelFrame(f, text="Giao hàng", padding=8)
        left.grid(row=1, column=0, sticky="nsew", pady=8, padx=(0, 6))
        self.cbo_address = ChoiceBox(left, width=48)
        self.cbo_address.grid(row=0, column=0, sticky="we")
        self.btn_add_address = ttk.Button(left, text="Thêm địa chỉ", command=self.on_add_address)
        self.btn_add_address.grid(row=0, column=1, padx=4)
        self.var_delivery_service = tk.StringVar(value=DeliveryService.STANDARD.value)
        box = ttk.Frame(left)
        box.grid(row=1, column=0, columnspan=2, sticky="w", pady=4)
        self.rdo_delivery_service = []
        for d in DeliveryService:
            rb = ttk.Radiobutton(box, text=label(d), value=d.value, variable=self.var_delivery_service,
                                 command=self.on_change_delivery_service)
            rb.pack(side="left", padx=(0, 10))
            self.rdo_delivery_service.append(rb)
        ttk.Label(left, text="Ghi chú").grid(row=2, column=0, sticky="w")
        self.txt_note = ttk.Entry(left, width=50)
        self.txt_note.grid(row=3, column=0, columnspan=2, sticky="we")
        ttk.Label(left, text="Mã giảm giá").grid(row=4, column=0, sticky="w", pady=(8, 0))
        vbox = ttk.Frame(left)
        vbox.grid(row=5, column=0, columnspan=2, sticky="w")
        self.txt_voucher_code = ttk.Entry(vbox, width=20)
        self.txt_voucher_code.pack(side="left")
        self.btn_apply_voucher = ttk.Button(vbox, text="Áp dụng", command=self.on_apply_voucher)
        self.btn_apply_voucher.pack(side="left", padx=4)
        self.lbl_vouchers = ttk.Label(vbox, style="Success.TLabel")
        self.lbl_vouchers.pack(side="left")

        right = ttk.LabelFrame(f, text="Thanh toán", padding=8)
        right.grid(row=1, column=1, sticky="nsew", pady=8)
        self.var_payment_method = tk.StringVar(value=PaymentMethodType.COD.value)
        self.rdo_payment_method = []
        for i, m in enumerate(PaymentMethodType):
            rb = ttk.Radiobutton(right, text=label(m), value=m.value, variable=self.var_payment_method,
                                 command=self._on_change_payment_method)
            rb.grid(row=i, column=0, columnspan=2, sticky="w")
            self.rdo_payment_method.append(rb)
        ttk.Label(right, text="Phương thức đã liên kết").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.cbo_linked_method = ChoiceBox(right, width=26)
        self.cbo_linked_method.grid(row=5, column=0, columnspan=2, sticky="w")
        tot = ttk.Frame(right)
        tot.grid(row=6, column=0, columnspan=2, sticky="we", pady=(10, 0))
        self.lbl_subtotal, self.lbl_discount = ttk.Label(tot), ttk.Label(tot)
        self.lbl_shipping_fee, self.lbl_grand_total = ttk.Label(tot), ttk.Label(tot, style="H2.TLabel")
        for r, (t, w) in enumerate([("Tạm tính", self.lbl_subtotal), ("Giảm giá", self.lbl_discount),
                                    ("Phí vận chuyển", self.lbl_shipping_fee), ("Tổng cộng", self.lbl_grand_total)]):
            ttk.Label(tot, text=t).grid(row=r, column=0, sticky="w")
            w.grid(row=r, column=1, sticky="e", padx=(20, 0))
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=2, column=0, columnspan=2, sticky="w")
        bar = ttk.Frame(f)
        bar.grid(row=3, column=0, columnspan=2, sticky="e")
        self.btn_back = ttk.Button(bar, text="Quay lại giỏ", command=self.on_back)
        self.btn_back.pack(side="left", padx=4)
        self.btn_place_order = ttk.Button(bar, text="Đặt hàng", command=self.on_place_order)
        self.btn_place_order.pack(side="left")
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)

    def _load_addresses(self, select_id: int | None = None) -> None:
        self.list_address = self.checkout_controller.get_addresses(self.customer)
        self.cbo_address.set_choices([(f"{a.recipient_name} – {a.phone} – {a.one_line()}", a) for a in self.list_address])
        if select_id is not None:
            self.cbo_address.select_value(Address(id=select_id), key=lambda a: a.id)

    def _show_totals(self) -> None:
        o = self.order
        fill_table(self.tbl_order_item, [(k, (i.sku, i.style_name, f"{i.colour}/{i.size_label}", i.quantity,
                                              money(i.unit_price), money(i.discount), money(i.line_total)))
                                         for k, i in enumerate(o.items)])
        self.lbl_subtotal.config(text=money(o.subtotal))
        self.lbl_discount.config(text="−" + money(o.discount))
        self.lbl_shipping_fee.config(text=money(o.shipping_fee) if o.shipping_fee else "Miễn phí")
        self.lbl_grand_total.config(text=money(o.grand_total))
        self.lbl_vouchers.config(text=", ".join(v.code for v in self.list_voucher))

    @guarded
    def on_add_address(self) -> None:
        frm = EditAddressFrm(self.customer, None)
        modal(frm, self)
        self._load_addresses(frm.address.id if frm.address and frm.address.id else None)

    @guarded
    def on_change_delivery_service(self) -> None:
        self.order.delivery_service = DeliveryService(self.var_delivery_service.get())
        self.checkout_controller.recalc(self.order)
        self._show_totals()

    def _on_change_payment_method(self) -> None:
        options = self.checkout_controller.get_payment_options(self.customer,
                                                               PaymentMethodType(self.var_payment_method.get()))
        self.list_payment_method = [m for m in options if m is not None]
        self.cbo_linked_method.set_choices([(f"{m.provider} {m.masked_number}" if m else
                                             "Ví chưa liên kết (thanh toán trên ví)", m) for m in options])
        self.cbo_linked_method.state(["!disabled"] if options else ["disabled"])

    @guarded
    def on_apply_voucher(self) -> None:
        voucher = self.checkout_controller.apply_voucher(self.order, self.txt_voucher_code.get())
        self.txt_voucher_code.delete(0, "end")
        self._show_totals()
        show(self.lbl_message, f"Đã áp dụng mã {voucher.code}", ok=True)

    @guarded
    def on_place_order(self) -> None:
        o = self.order
        o.delivery_service = DeliveryService(self.var_delivery_service.get())
        try:
            self.checkout_controller.place_order(self.customer, o, self.cbo_address.value(),
                                                 PaymentMethodType(self.var_payment_method.get()),
                                                 self.cbo_linked_method.value(), self.txt_note.get())
        except ServiceUnavailable as e:    # đơn đã giữ hàng: sang màn hình kết quả để thanh toán lại, không đặt trùng
            self.destroy()
            warn(ConfirmOrderFrm(self.customer, o), f"Cổng thanh toán tạm thời không phản hồi ({e}). "
                                                     "Đơn đã được giữ, hãy bấm thanh toán lại.")
            return
        finally:
            self.order_placed = o.id is not None
        self.destroy()
        ConfirmOrderFrm(self.customer, o)

    def on_back(self) -> None:
        self.destroy()
