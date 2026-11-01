# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.register_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.customer_dao import CustomerDAO


class RegisterFrm(tk.Toplevel):
    """RegisterFrm -- layer abc_fashion.view.account.
    Uses (control layer): CustomerDAO
    Opens (view layer): AdminHomeFrm
    """

    txt_full_name: ttk.Entry
    txt_email: ttk.Entry
    txt_phone: ttk.Entry
    txt_password: ttk.Entry
    txt_confirm_password: ttk.Entry
    chk_marketing_consent: ttk.Checkbutton
    btn_register: ttk.Button
    btn_cancel: ttk.Button
    lbl_message: ttk.Label

    def __init__(self):
        super().__init__()
        self.customer_dao = CustomerDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_register(self):
        raise NotImplementedError

    def on_cancel(self):
        raise NotImplementedError
