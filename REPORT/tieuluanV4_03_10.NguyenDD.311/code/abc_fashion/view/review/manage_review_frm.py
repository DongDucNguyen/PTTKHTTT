# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.review.manage_review_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.review_dao import ReviewDAO
from abc_fashion.model.review import tblReview
from abc_fashion.model.user import tblStaffMember


class ManageReviewFrm(tk.Toplevel):
    """ManageReviewFrm -- layer abc_fashion.view.review.
    Uses (control layer): ReviewDAO
    Holds (model layer): tblReview, tblStaffMember
    """

    staff: tblStaffMember
    list_review: list[tblReview]
    cbo_status: ttk.Combobox
    txt_keyword: ttk.Entry
    spn_rating: ttk.Spinbox
    btn_search: ttk.Button
    tbl_review: ttk.Treeview
    txa_body: tk.Text
    txt_moderation_note: ttk.Entry
    btn_approve: ttk.Button
    btn_reject: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.review_dao = ReviewDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_select_review(self):
        raise NotImplementedError

    def on_approve(self):
        raise NotImplementedError

    def on_reject(self):
        raise NotImplementedError
