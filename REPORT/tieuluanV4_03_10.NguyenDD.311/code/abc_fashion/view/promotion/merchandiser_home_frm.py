# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.promotion.merchandiser_home_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import tblStaffMember


class MerchandiserHomeFrm(tk.Toplevel):
    """MerchandiserHomeFrm -- layer abc_fashion.view.promotion.
    Opens (view layer): ManagePromotionFrm
    Holds (model layer): tblStaffMember
    """

    staff: tblStaffMember
    btn_manage_promotion: ttk.Button
    btn_view_report: ttk.Button
    btn_logout: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        raise NotImplementedError  # create and place the ttk widgets

    def on_manage_promotion(self):
        raise NotImplementedError

    def on_view_report(self):
        raise NotImplementedError

    def on_logout(self):
        raise NotImplementedError
