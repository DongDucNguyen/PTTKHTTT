# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.report.sales_detail_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import date, datetime

from abc_fashion.control.dao.order_item_dao import OrderItemDAO
from abc_fashion.model.sales import tblOrderItem
from abc_fashion.model.stat import StyleStat


class SalesDetailFrm(tk.Toplevel):
    """SalesDetailFrm -- layer abc_fashion.view.report.
    Uses (control layer): OrderItemDAO
    Holds (model layer): tblOrderItem, StyleStat
    """

    style_stat: StyleStat
    list_order_item: list[tblOrderItem]
    lbl_style_name: ttk.Label
    lbl_period: ttk.Label
    tbl_order_item: ttk.Treeview

    def __init__(self, style_stat: StyleStat, start: date, end: date):
        super().__init__()
        self.style_stat = style_stat
        self.start = start
        self.end = end
        self.order_item_dao = OrderItemDAO()
        raise NotImplementedError  # create and place the ttk widgets
