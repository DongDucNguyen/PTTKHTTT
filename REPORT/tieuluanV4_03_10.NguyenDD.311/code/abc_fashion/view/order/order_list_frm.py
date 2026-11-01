# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order.order_list_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblCustomer


class OrderListFrm(tk.Toplevel):
    """OrderListFrm -- layer abc_fashion.view.order.
    Uses (control layer): OrderDAO
    Opens (view layer): OrderDetailFrm
    Holds (model layer): tblCustomer, tblOrder
    """

    customer: tblCustomer
    list_order: list[tblOrder]
    cbo_status: ttk.Combobox
    btn_filter: ttk.Button
    tbl_order: ttk.Treeview

    def __init__(self, customer: tblCustomer):
        super().__init__()
        self.customer = customer
        self.order_dao = OrderDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_filter(self):
        raise NotImplementedError

    def on_open_order(self):
        raise NotImplementedError
