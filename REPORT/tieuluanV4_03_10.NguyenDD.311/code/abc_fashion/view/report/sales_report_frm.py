# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.report.sales_report_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.style_stat_dao import StyleStatDAO
from abc_fashion.model.stat import StyleStat
from abc_fashion.model.user import tblStaffMember


class SalesReportFrm(tk.Toplevel):
    """SalesReportFrm -- layer abc_fashion.view.report.
    Uses (control layer): StyleStatDAO
    Opens (view layer): SalesDetailFrm
    Holds (model layer): tblStaffMember, StyleStat
    """

    staff: tblStaffMember
    list_style_stat: list[StyleStat]
    dte_from: DateEntry
    dte_to: DateEntry
    cbo_category: ttk.Combobox
    cbo_collection: ttk.Combobox
    btn_view: ttk.Button
    tbl_style_stat: ttk.Treeview
    lbl_total_revenue: ttk.Label
    btn_export: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.style_stat_dao = StyleStatDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_view(self):
        raise NotImplementedError

    def on_open_detail(self):
        raise NotImplementedError

    def on_export(self):
        raise NotImplementedError
