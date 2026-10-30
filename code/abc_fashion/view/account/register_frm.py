"""RegisterFrm — Đăng ký tài khoản khách (UC01)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.auth_controller import AuthController
from abc_fashion.model.user import Customer
from abc_fashion.view._util import body, button_row, entry_set, form_rows, guarded, info, message_label


class RegisterFrm(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self._build()

    def _build(self) -> None:
        f = body(self, "Đăng ký")
        self.txt_full_name = ttk.Entry(f, width=34)
        self.txt_email = ttk.Entry(f, width=34)
        self.txt_phone = ttk.Entry(f, width=34)
        self.txt_password = ttk.Entry(f, width=34, show="*")
        self.txt_confirm_password = ttk.Entry(f, width=34, show="*")
        self.var_marketing_consent = tk.BooleanVar(value=False)
        self.chk_marketing_consent = ttk.Checkbutton(f, text="Nhận tin khuyến mãi", variable=self.var_marketing_consent)
        r = form_rows(f, [("Họ tên", self.txt_full_name), ("E-mail", self.txt_email), ("Điện thoại", self.txt_phone),
                          ("Mật khẩu", self.txt_password), ("Nhập lại mật khẩu", self.txt_confirm_password),
                          ("", self.chk_marketing_consent)])
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=r, column=0, columnspan=2, sticky="w")
        self.btn_register = ttk.Button(f, text="Đăng ký", command=self.on_register)
        self.btn_cancel = ttk.Button(f, text="Huỷ", command=self.on_cancel)
        button_row(f, [self.btn_cancel, self.btn_register], r + 1)
        self.txt_full_name.focus_set()

    @guarded
    def on_register(self) -> None:
        customer = Customer(email=self.txt_email.get(), password=self.txt_password.get(),
                            full_name=self.txt_full_name.get(), phone=self.txt_phone.get(),
                            marketing_consent=self.var_marketing_consent.get())
        self.auth_controller.register(customer, self.txt_confirm_password.get())
        info(self, "Đăng ký thành công. Mời bạn đăng nhập.")
        from abc_fashion.view.account import login_frm
        if login_frm.CURRENT_LOGIN is not None:
            entry_set(login_frm.CURRENT_LOGIN.txt_email, customer.email)
            login_frm.CURRENT_LOGIN.txt_password.focus_set()
        self.destroy()

    def on_cancel(self) -> None:
        self.destroy()
