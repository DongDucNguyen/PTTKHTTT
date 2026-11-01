# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.report.marketing_home_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import tblStaffMember


class MarketingHomeFrm(tk.Toplevel):
    """MarketingHomeFrm -- layer abc_fashion.view.report.
    Opens (view layer): SelectReportFrm
    Holds (model layer): tblStaffMember
    """

    staff: tblStaffMember
    btn_view_report: ttk.Button
    btn_logout: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        raise NotImplementedError  # create and place the ttk widgets

    def on_view_report(self):
        raise NotImplementedError

    def on_logout(self):
        raise NotImplementedError
