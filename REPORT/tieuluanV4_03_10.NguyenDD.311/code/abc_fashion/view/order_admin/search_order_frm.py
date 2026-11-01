# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order_admin.search_order_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblStaffMember


class SearchOrderFrm(tk.Toplevel):
    """SearchOrderFrm -- layer abc_fashion.view.order_admin.
    Uses (control layer): OrderDAO
    Opens (view layer): ManageOrderFrm
    Holds (model layer): tblOrder, tblStaffMember
    """

    staff: tblStaffMember
    list_order: list[tblOrder]
    txt_keyword: ttk.Entry
    cbo_status: ttk.Combobox
    dte_from: DateEntry
    dte_to: DateEntry
    btn_search: ttk.Button
    tbl_order: ttk.Treeview

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.order_dao = OrderDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_open_order(self):
        raise NotImplementedError
