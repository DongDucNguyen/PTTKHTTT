"""LinkPaymentMethodFrm — Liên kết thẻ / ví / tài khoản ngân hàng (UC03)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.profile_controller import ProfileController
from abc_fashion.model.customer_data import LinkedMethodType
from abc_fashion.model.user import Customer
from abc_fashion.view._util import ChoiceBox, body, button_row, enum_choices, form_rows, guarded, info, message_label


class LinkPaymentMethodFrm(tk.Toplevel):
    def __init__(self, customer: Customer):
        super().__init__()
        self.customer = customer
        self.profile_controller = ProfileController()
        self._build()
        self._on_type()

    def _build(self) -> None:
        f = body(self, "Liên kết phương thức thanh toán")
        self.cbo_method_type = ChoiceBox(f, enum_choices(LinkedMethodType))
        self.cbo_method_type.bind("<<ComboboxSelected>>", lambda e: self._on_type())
        self.cbo_provider = ChoiceBox(f)
        self.var_is_default = tk.BooleanVar()
        self.chk_is_default = ttk.Checkbutton(f, text="Đặt làm mặc định", variable=self.var_is_default)
        r = form_rows(f, [("Loại", self.cbo_method_type), ("Nhà cung cấp", self.cbo_provider), ("", self.chk_is_default)])
        ttk.Label(f, text="Số thẻ / tài khoản được nhập trên trang của cổng thanh toán;\n"
                          "ABC Fashion chỉ lưu số đã che.", style="Muted.TLabel").grid(row=r, column=0, columnspan=2,
                                                                                     sticky="w", pady=6)
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=r + 1, column=0, columnspan=2, sticky="w")
        self.btn_cancel = ttk.Button(f, text="Huỷ", command=self.on_cancel)
        self.btn_link = ttk.Button(f, text="Liên kết", command=self.on_link)
        button_row(f, [self.btn_cancel, self.btn_link], r + 2)

    def _on_type(self) -> None:
        self.cbo_provider.set_choices([(p, p) for p in self.profile_controller.get_providers(self.cbo_method_type.value())])

    @guarded
    def on_link(self) -> None:
        method = self.profile_controller.link_payment_method(self.customer, self.cbo_method_type.value(),
                                                             self.cbo_provider.value(), self.var_is_default.get())
        info(self, f"Đã liên kết {method.provider} {method.masked_number}")
        self.destroy()

    def on_cancel(self) -> None:
        self.destroy()
