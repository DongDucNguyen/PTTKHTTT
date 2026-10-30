"""EditAddressFrm — Thêm / sửa một địa chỉ. `address = None` → thêm mới."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.profile_controller import ProfileController
from abc_fashion.model.customer_data import Address
from abc_fashion.model.user import Customer
from abc_fashion.view._util import body, button_row, entry_set, form_rows, guarded, message_label


class EditAddressFrm(tk.Toplevel):
    def __init__(self, customer: Customer, address: Address | None):
        super().__init__()
        self.customer = customer
        self.address = address
        self.profile_controller = ProfileController()
        self._build()
        self.on_reset()

    def _build(self) -> None:
        f = body(self, "Địa chỉ")
        self.txt_recipient_name = ttk.Entry(f, width=34)
        self.txt_phone = ttk.Entry(f, width=34)
        self.txt_street = ttk.Entry(f, width=34)
        self.txt_ward = ttk.Entry(f, width=34)
        self.txt_district = ttk.Entry(f, width=34)
        self.txt_city = ttk.Entry(f, width=34)
        self.var_is_default = tk.BooleanVar()
        self.chk_is_default = ttk.Checkbutton(f, text="Đặt làm mặc định", variable=self.var_is_default)
        r = form_rows(f, [("Người nhận", self.txt_recipient_name), ("Điện thoại", self.txt_phone),
                          ("Số nhà, đường", self.txt_street), ("Phường / xã", self.txt_ward),
                          ("Quận / huyện", self.txt_district), ("Tỉnh / thành phố", self.txt_city),
                          ("", self.chk_is_default)])
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=r, column=0, columnspan=2, sticky="w")
        self.btn_reset = ttk.Button(f, text="Khôi phục", command=self.on_reset)
        self.btn_save = ttk.Button(f, text="Lưu", command=self.on_save)
        button_row(f, [self.btn_reset, self.btn_save], r + 1)

    @guarded
    def on_save(self) -> None:
        a = Address(id=self.address.id if self.address else None, recipient_name=self.txt_recipient_name.get(),
                    phone=self.txt_phone.get(), street=self.txt_street.get(), ward=self.txt_ward.get(),
                    district=self.txt_district.get(), city=self.txt_city.get(), is_default=self.var_is_default.get())
        self.profile_controller.save_address(self.customer, a)
        self.address = a
        self.destroy()

    def on_reset(self) -> None:
        a = self.address or Address(recipient_name=self.customer.full_name, phone=self.customer.phone)
        for w, v in ((self.txt_recipient_name, a.recipient_name), (self.txt_phone, a.phone), (self.txt_street, a.street),
                     (self.txt_ward, a.ward), (self.txt_district, a.district), (self.txt_city, a.city)):
            entry_set(w, v)
        self.var_is_default.set(bool(a.is_default))
        self.lbl_message.config(text="")
