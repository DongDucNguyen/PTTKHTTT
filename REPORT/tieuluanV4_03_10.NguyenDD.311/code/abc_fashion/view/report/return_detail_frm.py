# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.report.return_detail_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import date, datetime

from abc_fashion.control.dao.return_item_dao import ReturnItemDAO
from abc_fashion.model.returns import tblReturnItem
from abc_fashion.model.stat import ReturnStat


class ReturnDetailFrm(tk.Toplevel):
    """ReturnDetailFrm -- layer abc_fashion.view.report.
    Uses (control layer): ReturnItemDAO
    Holds (model layer): tblReturnItem, ReturnStat
    """

    return_stat: ReturnStat
    list_return_item: list[tblReturnItem]
    lbl_style_name: ttk.Label
    tbl_return_item: ttk.Treeview

    def __init__(self, return_stat: ReturnStat, start: date, end: date):
        super().__init__()
        self.return_stat = return_stat
        self.start = start
        self.end = end
        self.return_item_dao = ReturnItemDAO()
        raise NotImplementedError  # create and place the ttk widgets
