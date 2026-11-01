# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.customer_home_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import tblCustomer


class CustomerHomeFrm(tk.Toplevel):
    """CustomerHomeFrm -- layer abc_fashion.view.account.
    Opens (view layer): ProfileFrm, BrowseStyleFrm, SearchStyleFrm, CartFrm, OrderListFrm
    Holds (model layer): tblCustomer
    """

    customer: tblCustomer
    txt_keyword: ttk.Entry
    btn_search: ttk.Button
    btn_search_by_image: ttk.Button
    btn_browse: ttk.Button
    btn_cart: ttk.Button
    btn_orders: ttk.Button
    btn_profile: ttk.Button
    btn_logout: ttk.Button

    def __init__(self, customer: tblCustomer):
        super().__init__()
        self.customer = customer
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_search_by_image(self):
        raise NotImplementedError

    def on_browse(self):
        raise NotImplementedError

    def on_cart(self):
        raise NotImplementedError

    def on_orders(self):
        raise NotImplementedError

    def on_profile(self):
        raise NotImplementedError

    def on_logout(self):
        raise NotImplementedError
