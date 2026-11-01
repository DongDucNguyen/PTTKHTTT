# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.link_payment_method_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.payment_method_dao import PaymentMethodDAO
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.model.user import tblCustomer


class LinkPaymentMethodFrm(tk.Toplevel):
    """LinkPaymentMethodFrm -- layer abc_fashion.view.account.
    Uses (control layer): PaymentMethodDAO, PaymentGateway
    Holds (model layer): tblCustomer
    """

    customer: tblCustomer
    cbo_method_type: ttk.Combobox
    cbo_provider: ttk.Combobox
    chk_is_default: ttk.Checkbutton
    btn_link: ttk.Button
    btn_cancel: ttk.Button

    def __init__(self, customer: tblCustomer):
        super().__init__()
        self.customer = customer
        self.payment_method_dao = PaymentMethodDAO()
        self.payment_gateway = PaymentGateway()
        raise NotImplementedError  # create and place the ttk widgets

    def on_link(self):
        raise NotImplementedError

    def on_cancel(self):
        raise NotImplementedError
