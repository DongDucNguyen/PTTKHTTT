# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.search_account_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.user_dao import UserDAO
from abc_fashion.model.user import tblStaffMember, tblUser


class SearchAccountFrm(tk.Toplevel):
    """SearchAccountFrm -- layer abc_fashion.view.account.
    Uses (control layer): UserDAO
    Opens (view layer): EditAccountFrm
    Holds (model layer): tblStaffMember, tblUser
    """

    staff: tblStaffMember
    list_user: list[tblUser]
    txt_keyword: ttk.Entry
    cbo_user_type: ttk.Combobox
    cbo_status: ttk.Combobox
    btn_search: ttk.Button
    tbl_user: ttk.Treeview

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.user_dao = UserDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_select_user(self):
        raise NotImplementedError
