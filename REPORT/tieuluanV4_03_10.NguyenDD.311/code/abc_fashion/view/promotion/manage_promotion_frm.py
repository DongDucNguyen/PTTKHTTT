# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.promotion.manage_promotion_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.promotion_dao import PromotionDAO
from abc_fashion.model.sales import tblPromotion
from abc_fashion.model.user import tblStaffMember


class ManagePromotionFrm(tk.Toplevel):
    """ManagePromotionFrm -- layer abc_fashion.view.promotion.
    Uses (control layer): PromotionDAO
    Opens (view layer): EditPromotionFrm
    Holds (model layer): tblPromotion, tblStaffMember
    """

    staff: tblStaffMember
    list_promotion: list[tblPromotion]
    txt_keyword: ttk.Entry
    cbo_status: ttk.Combobox
    btn_search: ttk.Button
    tbl_promotion: ttk.Treeview
    btn_add: ttk.Button
    btn_edit: ttk.Button
    btn_end: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.promotion_dao = PromotionDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_add(self):
        raise NotImplementedError

    def on_edit(self):
        raise NotImplementedError

    def on_end(self):
        raise NotImplementedError
