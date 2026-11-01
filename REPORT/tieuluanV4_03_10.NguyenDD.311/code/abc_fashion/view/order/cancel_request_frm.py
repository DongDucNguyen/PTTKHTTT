# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order.cancel_request_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.model.sales import tblOrder


class CancelRequestFrm(tk.Toplevel):
    """CancelRequestFrm -- layer abc_fashion.view.order.
    Uses (control layer): OrderDAO
    Holds (model layer): tblOrder
    """

    order: tblOrder
    lbl_order_no: ttk.Label
    cbo_reason: ttk.Combobox
    txt_reason_detail: ttk.Entry
    btn_send: ttk.Button
    btn_back: ttk.Button

    def __init__(self, order: tblOrder):
        super().__init__()
        self.order = order
        self.order_dao = OrderDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_send(self):
        raise NotImplementedError

    def on_back(self):
        raise NotImplementedError
