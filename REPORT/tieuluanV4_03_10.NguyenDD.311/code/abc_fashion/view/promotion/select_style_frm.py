# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.promotion.select_style_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.model.catalogue import tblStyle


class SelectStyleFrm(tk.Toplevel):
    """SelectStyleFrm -- layer abc_fashion.view.promotion.
    Uses (control layer): StyleDAO
    Holds (model layer): tblStyle
    """

    list_style: list[tblStyle]
    list_selected: list[tblStyle]
    txt_keyword: ttk.Entry
    cbo_category: ttk.Combobox
    btn_search: ttk.Button
    tbl_style: ttk.Treeview
    btn_select: ttk.Button

    def __init__(self, selected: list[tblStyle]):
        super().__init__()
        self.selected = selected
        self.style_dao = StyleDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_select(self):
        raise NotImplementedError
