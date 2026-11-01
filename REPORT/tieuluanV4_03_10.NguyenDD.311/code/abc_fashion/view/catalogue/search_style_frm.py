# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.catalogue.search_style_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.control.gateway.search_engine import SearchEngine
from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.user import tblCustomer


class SearchStyleFrm(tk.Toplevel):
    """SearchStyleFrm -- layer abc_fashion.view.catalogue.
    Uses (control layer): StyleDAO, SearchEngine
    Opens (view layer): StyleDetailFrm
    Holds (model layer): tblCustomer, tblStyle
    """

    customer: tblCustomer | None
    list_style: list[tblStyle]
    txt_keyword: ttk.Entry
    btn_search: ttk.Button
    btn_search_by_image: ttk.Button
    btn_search_by_voice: ttk.Button
    cnv_query_image: tk.Canvas
    tbl_style: ttk.Treeview
    lbl_message: ttk.Label

    def __init__(self, customer: tblCustomer | None, keyword: str):
        super().__init__()
        self.customer = customer
        self.keyword = keyword
        self.style_dao = StyleDAO()
        self.search_engine = SearchEngine()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_search_by_image(self):
        raise NotImplementedError

    def on_search_by_voice(self):
        raise NotImplementedError

    def on_open_style(self):
        raise NotImplementedError
