# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order.return_request_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.model.returns import tblReturnEvidence, tblReturnRequest
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblCustomer


class ReturnRequestFrm(tk.Toplevel):
    """ReturnRequestFrm -- layer abc_fashion.view.order.
    Uses (control layer): ReturnRequestDAO
    Holds (model layer): tblCustomer, tblOrder, tblReturnEvidence, tblReturnRequest
    """

    customer: tblCustomer
    order: tblOrder
    return_request: tblReturnRequest
    list_evidence: list[tblReturnEvidence]
    tbl_order_item: ttk.Treeview
    spn_quantity: ttk.Spinbox
    rdo_return_type: ttk.Radiobutton
    cbo_reason_code: ttk.Combobox
    txa_reason_detail: tk.Text
    rdo_desired_resolution: ttk.Radiobutton
    btn_add_evidence: ttk.Button
    tbl_evidence: ttk.Treeview
    btn_submit: ttk.Button

    def __init__(self, customer: tblCustomer, order: tblOrder):
        super().__init__()
        self.customer = customer
        self.order = order
        self.return_request_dao = ReturnRequestDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_select_item(self):
        raise NotImplementedError

    def on_add_evidence(self):
        raise NotImplementedError

    def on_submit(self):
        raise NotImplementedError
