# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.report.return_report_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.return_stat_dao import ReturnStatDAO
from abc_fashion.model.stat import ReturnStat
from abc_fashion.model.user import tblStaffMember


class ReturnReportFrm(tk.Toplevel):
    """ReturnReportFrm -- layer abc_fashion.view.report.
    Uses (control layer): ReturnStatDAO
    Opens (view layer): ReturnDetailFrm
    Holds (model layer): tblStaffMember, ReturnStat
    """

    staff: tblStaffMember
    list_return_stat: list[ReturnStat]
    dte_from: DateEntry
    dte_to: DateEntry
    cbo_reason: ttk.Combobox
    btn_view: ttk.Button
    tbl_return_stat: ttk.Treeview

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.return_stat_dao = ReturnStatDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_view(self):
        raise NotImplementedError

    def on_open_detail(self):
        raise NotImplementedError
