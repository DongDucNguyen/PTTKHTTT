"""SearchAccountFrm — Tìm tài khoản (UC20)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.account_admin_controller import AccountAdminController
from abc_fashion.model.user import AccountStatus, StaffMember, User
from abc_fashion.view._util import (ChoiceBox, body, enum_choices, fill_table, fmt_dt, guarded, label, make_table,
                                    modal, selected, warn)
from abc_fashion.view.account.edit_account_frm import EditAccountFrm, label_type


class SearchAccountFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_user: list[User] = []
        self.account_admin_controller = AccountAdminController()
        self._build()
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Quản lý tài khoản")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.txt_keyword = ttk.Entry(bar, width=28)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.cbo_user_type = ChoiceBox(bar, [("Tất cả", ""), ("Khách", "customer"), ("Nhân viên", "staff"),
                                             ("Nhà cung cấp", "supplier")], width=14)
        self.cbo_user_type.pack(side="left", padx=4)
        self.cbo_status = ChoiceBox(bar, enum_choices(AccountStatus, "Mọi trạng thái"), width=14)
        self.cbo_status.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_user = make_table(f, [("email", "E-mail", 200), ("name", "Họ tên", 160), ("type", "Loại", 110),
                                       ("status", "Trạng thái", 90), ("login", "Đăng nhập cuối", 130)], height=14)
        self.tbl_user.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_user.bind("<Double-1>", lambda e: self.on_select_user())
        ttk.Button(f, text="Mở tài khoản", command=self.on_select_user).grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_user = self.account_admin_controller.search_user(self.txt_keyword.get(), self.cbo_user_type.value(),
                                                                   self.cbo_status.value())
        fill_table(self.tbl_user, [(u.id, (u.email, getattr(u, "full_name", "") or "",
                                           label_type(getattr(u, "user_type", "")), label(u.status),
                                           fmt_dt(u.last_login_at)),
                                    ("bad",) if u.status == AccountStatus.SUSPENDED else ())
                                   for u in self.list_user])

    @guarded
    def on_select_user(self) -> None:
        u = selected(self.tbl_user, self.list_user)
        if u is None:
            return warn(self, "Chọn một tài khoản")
        modal(EditAccountFrm(self.staff, u), self)
        self.on_search()
