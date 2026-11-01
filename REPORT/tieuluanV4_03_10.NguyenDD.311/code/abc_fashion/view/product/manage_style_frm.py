# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.product.manage_style_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.user import tblStaffMember


class ManageStyleFrm(tk.Toplevel):
    """ManageStyleFrm -- layer abc_fashion.view.product.
    Uses (control layer): StyleDAO
    Opens (view layer): EditStyleFrm
    Holds (model layer): tblStaffMember, tblStyle
    """

    staff: tblStaffMember
    list_style: list[tblStyle]
    txt_keyword: ttk.Entry
    cbo_category: ttk.Combobox
    cbo_status: ttk.Combobox
    btn_search: ttk.Button
    tbl_style: ttk.Treeview
    btn_add: ttk.Button
    btn_edit: ttk.Button
    btn_deactivate: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.style_dao = StyleDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_add(self):
        raise NotImplementedError

    def on_edit(self):
        raise NotImplementedError

    def on_deactivate(self):
        raise NotImplementedError
