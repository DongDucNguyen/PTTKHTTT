# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.checkout.confirm_order_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblCustomer


class ConfirmOrderFrm(tk.Toplevel):
    """ConfirmOrderFrm -- layer abc_fashion.view.checkout.
    Uses (control layer): PaymentDAO, PaymentGateway
    Holds (model layer): tblCustomer, tblOrder
    """

    customer: tblCustomer
    order: tblOrder
    lbl_order_no: ttk.Label
    lbl_status: ttk.Label
    tbl_order_item: ttk.Treeview
    tbl_shipment: ttk.Treeview
    lbl_grand_total: ttk.Label
    lbl_payment_result: ttk.Label
    btn_retry_payment: ttk.Button
    btn_view_order: ttk.Button
    btn_continue_shopping: ttk.Button

    def __init__(self, customer: tblCustomer, order: tblOrder):
        super().__init__()
        self.customer = customer
        self.order = order
        self.payment_dao = PaymentDAO()
        self.payment_gateway = PaymentGateway()
        raise NotImplementedError  # create and place the ttk widgets

    def on_retry_payment(self):
        raise NotImplementedError

    def on_view_order(self):
        raise NotImplementedError

    def on_continue_shopping(self):
        raise NotImplementedError
