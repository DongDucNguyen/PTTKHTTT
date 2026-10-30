"""CartFrm — Giỏ hàng (UC07)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.cart_controller import CartController
from abc_fashion.model.sales import Cart
from abc_fashion.model.user import Customer
from abc_fashion.view._util import (body, confirm, fill_table, guarded, make_table, message_label, modal, money,
                                    selected, show, warn)
from abc_fashion.view.checkout.checkout_frm import CheckoutFrm


class CartFrm(tk.Toplevel):
    def __init__(self, customer: Customer):
        super().__init__()
        self.customer = customer
        self.cart: Cart | None = None
        self.cart_controller = CartController()
        self._bad: set[int] = set()
        self._build()
        self._reload()

    def _build(self) -> None:
        f = body(self, "Giỏ hàng")
        self.tbl_cart_item = make_table(f, [("sku", "SKU", 100), ("name", "Sản phẩm", 200), ("colour", "Màu", 70),
                                            ("size", "Cỡ", 50), ("price", "Đơn giá", 90), ("qty", "SL", 40),
                                            ("total", "Thành tiền", 100)], height=10)
        self.tbl_cart_item.box.grid(row=0, column=0, columnspan=5, sticky="nsew")
        self.tbl_cart_item.bind("<<TreeviewSelect>>", lambda e: self._on_select())
        ttk.Label(f, text="Số lượng").grid(row=1, column=0, sticky="w", pady=6)
        self.spn_quantity = ttk.Spinbox(f, from_=0, to=99, width=5)
        self.spn_quantity.grid(row=1, column=1, sticky="w")
        self.btn_update_quantity = ttk.Button(f, text="Cập nhật", command=self.on_update_quantity)
        self.btn_update_quantity.grid(row=1, column=2, sticky="w")
        self.btn_remove_item = ttk.Button(f, text="Xoá dòng", command=self.on_remove_item)
        self.btn_remove_item.grid(row=1, column=3, sticky="w")
        self.lbl_subtotal = ttk.Label(f, style="H3.TLabel")
        self.lbl_subtotal.grid(row=1, column=4, sticky="e")
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=2, column=0, columnspan=5, sticky="w")
        self.btn_continue_shopping = ttk.Button(f, text="Tiếp tục mua", command=self.on_continue_shopping)
        self.btn_continue_shopping.grid(row=3, column=3, pady=8, sticky="e")
        self.btn_checkout = ttk.Button(f, text="Thanh toán", command=self.on_checkout)
        self.btn_checkout.grid(row=3, column=4, pady=8, sticky="e")
        f.rowconfigure(0, weight=1)
        f.columnconfigure(4, weight=1)

    def _reload(self) -> None:
        self.cart = self.cart_controller.get_cart(self.customer)
        fill_table(self.tbl_cart_item, [(i.id, (i.sku, i.style_name, i.colour, i.size_label, money(i.price), i.quantity,
                                                money(i.quantity * i.price)), ("bad",) if i.id in self._bad else ())
                                        for i in self.cart.items])
        self.lbl_subtotal.config(text=f"Tạm tính: {money(self.cart.subtotal)}")

    def _selected_item(self):
        return selected(self.tbl_cart_item, self.cart.items)

    def _on_select(self) -> None:
        item = self._selected_item()
        if item:
            self.spn_quantity.set(item.quantity)

    @guarded
    def on_update_quantity(self) -> None:
        item = self._selected_item()
        if item is None:
            return warn(self, "Chọn một dòng")
        try:
            n = int(self.spn_quantity.get())
        except ValueError:
            return show(self.lbl_message, "Số lượng không hợp lệ")
        if n == 0 and not confirm(self, f"Xoá {item.sku} khỏi giỏ?"):
            return
        self.cart_controller.update_quantity(item, n)
        self._bad.discard(item.id)
        self._reload()

    @guarded
    def on_remove_item(self) -> None:
        item = self._selected_item()
        if item is None:
            return warn(self, "Chọn một dòng")
        self.cart_controller.remove_item(item)
        self._reload()

    def on_continue_shopping(self) -> None:
        self.destroy()

    @guarded
    def on_checkout(self) -> None:
        self._reload()
        bad = self.cart_controller.check_availability(self.cart)                  # UC29
        self._bad = {b.id for b in bad}
        if bad:
            self._reload()
            return show(self.lbl_message, "Không đủ hàng: " + ", ".join(
                f"{b.sku} (còn {getattr(b, 'available', 0)})" for b in bad))
        show(self.lbl_message, "")
        frm = CheckoutFrm(self.customer, self.cart)
        modal(frm, self)
        if frm.order_placed:
            self.destroy()
        else:
            self._reload()
