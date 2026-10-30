"""EditAccountFrm — Khoá / mở / đặt lại mật khẩu / đổi vai trò (UC20)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.account_admin_controller import AccountAdminController
from abc_fashion.model.user import AccountStatus, StaffRole, StaffMember, User
from abc_fashion.view._util import ChoiceBox, body, confirm, enum_choices, fmt_dt, guarded, info, label


class EditAccountFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, user: User):
        super().__init__()
        self.staff = staff
        self.user = user
        self.account_admin_controller = AccountAdminController()
        self.staff_member: StaffMember | None = self.account_admin_controller.get_staff_member(user)
        self._build()
        self._refresh()

    def _build(self) -> None:
        f = body(self, "Tài khoản")
        self.lbl_email = ttk.Label(f)
        self.lbl_full_name = ttk.Label(f)
        self.lbl_status = ttk.Label(f)
        self.lbl_last_login_at = ttk.Label(f)
        for r, (t, w) in enumerate([("E-mail", self.lbl_email), ("Họ tên", self.lbl_full_name),
                                    ("Trạng thái", self.lbl_status), ("Đăng nhập cuối", self.lbl_last_login_at)]):
            ttk.Label(f, text=t).grid(row=r, column=0, sticky="w", pady=2)
            w.grid(row=r, column=1, columnspan=2, sticky="w")
        ttk.Label(f, text="Vai trò").grid(row=4, column=0, sticky="w")
        self.cbo_role = ChoiceBox(f, enum_choices(StaffRole), width=24)
        self.btn_save_role = ttk.Button(f, text="Lưu vai trò", command=self.on_save_role)
        if self.staff_member:
            self.cbo_role.grid(row=4, column=1, sticky="w")
            self.btn_save_role.grid(row=4, column=2, padx=4)
            self.cbo_role.select_value(self.staff_member.role)
        else:
            ttk.Label(f, text=label_type(getattr(self.user, "user_type", ""))).grid(row=4, column=1, sticky="w")
        bar = ttk.Frame(f)
        bar.grid(row=5, column=0, columnspan=3, pady=(12, 0), sticky="e")
        self.btn_suspend = ttk.Button(bar, text="Khoá tài khoản", command=self.on_suspend)
        self.btn_activate = ttk.Button(bar, text="Mở khoá", command=self.on_activate)
        self.btn_reset_password = ttk.Button(bar, text="Đặt lại mật khẩu", command=self.on_reset_password)
        for b in (self.btn_suspend, self.btn_activate, self.btn_reset_password):
            b.pack(side="left", padx=3)

    def _refresh(self) -> None:
        u = self.user
        self.lbl_email.config(text=u.email)
        self.lbl_full_name.config(text=getattr(u, "full_name", "") or "")
        self.lbl_status.config(text=label(u.status))
        self.lbl_last_login_at.config(text=fmt_dt(u.last_login_at) or "chưa đăng nhập")
        active = u.status == AccountStatus.ACTIVE
        self.btn_suspend.state(["!disabled"] if active else ["disabled"])
        self.btn_activate.state(["disabled"] if active else ["!disabled"])

    @guarded
    def on_suspend(self) -> None:
        if self.user.id != self.staff.userId and not confirm(self, f"Khoá tài khoản {self.user.email}?"):
            return
        self.account_admin_controller.suspend_account(self.staff, self.user)
        self._refresh()

    @guarded
    def on_activate(self) -> None:
        self.account_admin_controller.activate_account(self.staff, self.user)
        self._refresh()

    @guarded
    def on_reset_password(self) -> None:
        if not confirm(self, f"Đặt lại mật khẩu cho {self.user.email}?"):
            return
        temp = self.account_admin_controller.reset_password(self.staff, self.user)
        if temp:
            info(self, f"Mật khẩu tạm (chỉ hiện một lần): {temp}")

    @guarded
    def on_save_role(self) -> None:
        if self.staff_member is None:
            return
        if self.account_admin_controller.change_role(self.staff, self.staff_member, self.cbo_role.value()):
            info(self, "Đã đổi vai trò")


def label_type(user_type: str) -> str:
    return {"customer": "Khách hàng", "supplier": "Nhà cung cấp", "staff": "Nhân viên"}.get(user_type, "—")
