# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.login_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.user_dao import UserDAO


class LoginFrm(tk.Toplevel):
    """LoginFrm -- layer abc_fashion.view.account.
    Uses (control layer): UserDAO
    Opens (view layer): RegisterFrm, CustomerHomeFrm, AdminHomeFrm, ManagerHomeFrm, MerchandiserHomeFrm, WarehouseHomeFrm, CustomerServiceHomeFrm, SupplierHomeFrm, MarketingHomeFrm
    """

    txt_email: ttk.Entry
    txt_password: ttk.Entry
    btn_login: ttk.Button
    btn_register: ttk.Button
    lbl_message: ttk.Label

    def __init__(self):
        super().__init__()
        self.user_dao = UserDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_login(self):
        raise NotImplementedError

    def on_register(self):
        raise NotImplementedError
