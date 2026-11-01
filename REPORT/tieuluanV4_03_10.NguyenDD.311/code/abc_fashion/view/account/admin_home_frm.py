# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.admin_home_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import tblStaffMember


class AdminHomeFrm(tk.Toplevel):
    """AdminHomeFrm -- layer abc_fashion.view.account.
    Opens (view layer): SearchAccountFrm
    Holds (model layer): tblStaffMember
    """

    staff: tblStaffMember
    btn_manage_account: ttk.Button
    btn_manage_product: ttk.Button
    btn_manage_review: ttk.Button
    btn_view_audit_log: ttk.Button
    btn_logout: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        raise NotImplementedError  # create and place the ttk widgets

    def on_manage_account(self):
        raise NotImplementedError

    def on_manage_product(self):
        raise NotImplementedError

    def on_manage_review(self):
        raise NotImplementedError

    def on_view_audit_log(self):
        raise NotImplementedError

    def on_logout(self):
        raise NotImplementedError
