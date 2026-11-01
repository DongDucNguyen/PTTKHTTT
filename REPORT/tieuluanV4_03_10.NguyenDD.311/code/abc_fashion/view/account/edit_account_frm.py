# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.edit_account_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.staff_member_dao import StaffMemberDAO
from abc_fashion.control.dao.user_dao import UserDAO
from abc_fashion.model.user import tblStaffMember, tblUser


class EditAccountFrm(tk.Toplevel):
    """EditAccountFrm -- layer abc_fashion.view.account.
    Uses (control layer): UserDAO, StaffMemberDAO
    Opens (view layer): AuditLogFrm
    Holds (model layer): tblStaffMember, tblUser
    """

    staff: tblStaffMember
    user: tblUser
    lbl_email: ttk.Label
    lbl_full_name: ttk.Label
    lbl_status: ttk.Label
    lbl_last_login_at: ttk.Label
    cbo_role: ttk.Combobox
    btn_suspend: ttk.Button
    btn_activate: ttk.Button
    btn_reset_password: ttk.Button
    btn_save_role: ttk.Button

    def __init__(self, staff: tblStaffMember, user: tblUser):
        super().__init__()
        self.staff = staff
        self.user = user
        self.user_dao = UserDAO()
        self.staff_member_dao = StaffMemberDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_suspend(self):
        raise NotImplementedError

    def on_activate(self):
        raise NotImplementedError

    def on_reset_password(self):
        raise NotImplementedError

    def on_save_role(self):
        raise NotImplementedError
