# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.select_variant_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.model.catalogue import tblProductVariant


class SelectVariantFrm(tk.Toplevel):
    """SelectVariantFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): ProductVariantDAO
    Holds (model layer): tblProductVariant
    """

    list_variant: list[tblProductVariant]
    txt_keyword: ttk.Entry
    btn_search: ttk.Button
    tbl_variant: ttk.Treeview
    btn_select: ttk.Button

    def __init__(self):
        super().__init__()
        self.product_variant_dao = ProductVariantDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_select(self):
        raise NotImplementedError
