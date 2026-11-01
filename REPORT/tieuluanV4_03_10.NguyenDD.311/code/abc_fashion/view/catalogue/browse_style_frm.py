# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.catalogue.browse_style_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.category_dao import CategoryDAO
from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.model.catalogue import tblCategory, tblStyle
from abc_fashion.model.user import tblCustomer


class BrowseStyleFrm(tk.Toplevel):
    """BrowseStyleFrm -- layer abc_fashion.view.catalogue.
    Uses (control layer): CategoryDAO, StyleDAO
    Opens (view layer): StyleDetailFrm
    Holds (model layer): tblCategory, tblCustomer, tblStyle
    """

    customer: tblCustomer | None
    list_category: list[tblCategory]
    list_style: list[tblStyle]
    tree_category: ttk.Treeview
    cbo_size: ttk.Combobox
    cbo_colour: ttk.Combobox
    cbo_fit_type: ttk.Combobox
    txt_min_price: ttk.Entry
    txt_max_price: ttk.Entry
    cbo_sort: ttk.Combobox
    btn_filter: ttk.Button
    tbl_style: ttk.Treeview

    def __init__(self, customer: tblCustomer | None):
        super().__init__()
        self.customer = customer
        self.category_dao = CategoryDAO()
        self.style_dao = StyleDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_select_category(self):
        raise NotImplementedError

    def on_filter(self):
        raise NotImplementedError

    def on_open_style(self):
        raise NotImplementedError
