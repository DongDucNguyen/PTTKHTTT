# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.report.select_report_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import tblStaffMember


class SelectReportFrm(tk.Toplevel):
    """SelectReportFrm -- layer abc_fashion.view.report.
    Opens (view layer): SalesReportFrm, ReturnReportFrm
    Holds (model layer): tblStaffMember
    """

    staff: tblStaffMember
    cbo_report_type: ttk.Combobox
    btn_select: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        raise NotImplementedError  # create and place the ttk widgets

    def on_select(self):
        raise NotImplementedError
