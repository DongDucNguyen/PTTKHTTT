# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.checkout.cart_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.cart_dao import CartDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.model.sales import tblCart
from abc_fashion.model.user import tblCustomer


class CartFrm(tk.Toplevel):
    """CartFrm -- layer abc_fashion.view.checkout.
    Uses (control layer): CartDAO, StockLevelDAO
    Opens (view layer): CheckoutFrm
    Holds (model layer): tblCart, tblCustomer
    """

    customer: tblCustomer
    cart: tblCart
    tbl_cart_item: ttk.Treeview
    spn_quantity: ttk.Spinbox
    btn_update_quantity: ttk.Button
    btn_remove_item: ttk.Button
    lbl_subtotal: ttk.Label
    lbl_message: ttk.Label
    btn_continue_shopping: ttk.Button
    btn_checkout: ttk.Button

    def __init__(self, customer: tblCustomer):
        super().__init__()
        self.customer = customer
        self.cart_dao = CartDAO()
        self.stock_level_dao = StockLevelDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_update_quantity(self):
        raise NotImplementedError

    def on_remove_item(self):
        raise NotImplementedError

    def on_continue_shopping(self):
        raise NotImplementedError

    def on_checkout(self):
        raise NotImplementedError
