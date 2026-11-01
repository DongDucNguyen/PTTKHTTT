# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order.review_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.review_dao import ReviewDAO
from abc_fashion.control.gateway.assistant_engine import AssistantEngine
from abc_fashion.model.sales import tblOrderItem
from abc_fashion.model.user import tblCustomer


class ReviewFrm(tk.Toplevel):
    """ReviewFrm -- layer abc_fashion.view.order.
    Uses (control layer): ReviewDAO, AssistantEngine
    Holds (model layer): tblCustomer, tblOrderItem
    """

    customer: tblCustomer
    order_item: tblOrderItem
    lbl_style_name: ttk.Label
    lbl_variant: ttk.Label
    spn_rating: ttk.Spinbox
    txa_body: tk.Text
    txt_size_purchased: ttk.Entry
    rdo_fit_vote: ttk.Radiobutton
    btn_submit: ttk.Button
    lbl_message: ttk.Label

    def __init__(self, customer: tblCustomer, order_item: tblOrderItem):
        super().__init__()
        self.customer = customer
        self.order_item = order_item
        self.review_dao = ReviewDAO()
        self.assistant_engine = AssistantEngine()
        raise NotImplementedError  # create and place the ttk widgets

    def on_submit(self):
        raise NotImplementedError
