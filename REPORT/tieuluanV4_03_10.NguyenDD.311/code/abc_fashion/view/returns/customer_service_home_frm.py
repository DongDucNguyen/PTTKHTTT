# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.returns.customer_service_home_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import tblStaffMember


class CustomerServiceHomeFrm(tk.Toplevel):
    """CustomerServiceHomeFrm -- layer abc_fashion.view.returns.
    Opens (view layer): SearchReturnRequestFrm, ManageReviewFrm
    Holds (model layer): tblStaffMember
    """

    staff: tblStaffMember
    btn_process_return: ttk.Button
    btn_manage_review: ttk.Button
    btn_view_report: ttk.Button
    btn_logout: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        raise NotImplementedError  # create and place the ttk widgets

    def on_process_return(self):
        raise NotImplementedError

    def on_manage_review(self):
        raise NotImplementedError

    def on_view_report(self):
        raise NotImplementedError

    def on_logout(self):
        raise NotImplementedError
