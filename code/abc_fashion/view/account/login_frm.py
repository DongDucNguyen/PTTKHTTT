"""LoginFrm — Màn hình đầu tiên (UC02). Mọi vai trò đăng nhập ở đây."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.auth_controller import AuthController
from abc_fashion.model.user import StaffRole, Customer, Supplier
from abc_fashion.view import _art, _theme
from abc_fashion.view._util import body, guarded, message_label, show
from abc_fashion.view.account.admin_home_frm import AdminHomeFrm
from abc_fashion.view.account.customer_home_frm import CustomerHomeFrm
from abc_fashion.view.account.register_frm import RegisterFrm
from abc_fashion.view.inventory.supplier_home_frm import SupplierHomeFrm
from abc_fashion.view.inventory.warehouse_home_frm import WarehouseHomeFrm
from abc_fashion.view.order_admin.manager_home_frm import ManagerHomeFrm
from abc_fashion.view.promotion.merchandiser_home_frm import MerchandiserHomeFrm
from abc_fashion.view.report.marketing_home_frm import MarketingHomeFrm
from abc_fashion.view.returns.customer_service_home_frm import CustomerServiceHomeFrm

CURRENT_LOGIN: "LoginFrm | None" = None      # để trang chủ hiện lại khi đăng xuất

HOME = {StaffRole.ADMINISTRATOR: AdminHomeFrm, StaffRole.MANAGER: ManagerHomeFrm,
        StaffRole.MERCHANDISER: MerchandiserHomeFrm, StaffRole.MARKETING: MarketingHomeFrm,
        StaffRole.CUSTOMER_SERVICE: CustomerServiceHomeFrm, StaffRole.WAREHOUSE: WarehouseHomeFrm,
        StaffRole.SALES: MarketingHomeFrm}           # mục 13 #7: SALES tạm dùng trang marketing


class LoginFrm(tk.Toplevel):
    def __init__(self):
        super().__init__()
        global CURRENT_LOGIN
        CURRENT_LOGIN = self
        self.auth_controller = AuthController()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.bind("<Return>", lambda e: self.on_login())
        self.txt_email.focus_set()

    def _build(self) -> None:
        """uiux-design.md 7.1: tranh vector bên trái, thẻ đăng nhập bên phải."""
        f = body(self, "Đăng nhập", padding=0, header=False)
        art = _theme.image(self, "login_art", lambda sc: _art.login_art(360, 460, sc))
        tk.Label(f, image=art, borderwidth=0, background=_theme.INK_950).grid(row=0, column=0, sticky="nsew")
        form = ttk.Frame(f, padding=(_theme.px(self, 40), _theme.px(self, 36)))
        form.grid(row=0, column=1, sticky="nsew")
        brand = ttk.Frame(form)
        brand.grid(row=0, column=0, sticky="w")
        logo = _theme.image(self, "logo:48", lambda sc: _art.logo(48, sc))
        ttk.Label(brand, image=logo).pack(side="left", padx=(0, _theme.px(self, 12)))
        ttk.Label(brand, text="ABC Fashion", style="Display.TLabel").pack(side="left")
        ttk.Label(form, text="Thời trang cho mọi ngày — đăng nhập để tiếp tục", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(_theme.px(self, 6), _theme.px(self, 28)))
        gap = _theme.px(self, 4)
        ttk.Label(form, text="E-mail", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=(0, gap))
        self.txt_email = ttk.Entry(form, width=34)
        self.txt_email.grid(row=3, column=0, sticky="we", pady=(0, _theme.px(self, 14)))
        ttk.Label(form, text="Mật khẩu", style="Field.TLabel").grid(row=4, column=0, sticky="w", pady=(0, gap))
        self.txt_password = ttk.Entry(form, width=34, show="•")
        self.txt_password.grid(row=5, column=0, sticky="we")
        self.lbl_message = message_label(form)
        self.lbl_message.grid(row=6, column=0, sticky="w", pady=_theme.px(self, 8))
        self.btn_login = ttk.Button(form, text="Đăng nhập", command=self.on_login, style="Primary.TButton")
        self.btn_login.grid(row=7, column=0, sticky="we", ipady=_theme.px(self, 3))
        bottom = ttk.Frame(form)
        bottom.grid(row=8, column=0, sticky="we", pady=(_theme.px(self, 18), 0))
        ttk.Label(bottom, text="Chưa có tài khoản?", style="Muted.TLabel").pack(side="left")
        self.btn_register = ttk.Button(bottom, text="Đăng ký tài khoản khách", command=self.on_register,
                                       style="Link.TButton")
        self.btn_register.pack(side="left")
        form.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)
        self.resizable(False, False)

    @guarded
    def on_login(self) -> None:
        actor = self.auth_controller.login(self.txt_email.get(), self.txt_password.get())
        if isinstance(actor, Customer):
            home = CustomerHomeFrm(actor)
        elif isinstance(actor, Supplier):
            home = SupplierHomeFrm(actor)
        elif actor.role in HOME:
            home = HOME[actor.role](actor)
        else:
            return show(self.lbl_message, "Tài khoản chưa được gán vai trò")
        self.txt_password.delete(0, "end")
        self.lbl_message.config(text="")
        self.withdraw()
        home.protocol("WM_DELETE_WINDOW", home.on_logout)

    @guarded
    def on_register(self) -> None:
        RegisterFrm()
