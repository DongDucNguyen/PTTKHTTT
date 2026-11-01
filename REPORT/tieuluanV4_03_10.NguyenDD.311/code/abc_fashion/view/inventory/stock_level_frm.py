# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.stock_level_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.stock_location_dao import StockLocationDAO
from abc_fashion.model.inventory import tblStockLevel
from abc_fashion.model.user import tblStaffMember


class StockLevelFrm(tk.Toplevel):
    """StockLevelFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): StockLevelDAO, StockLocationDAO
    Opens (view layer): AdjustStockFrm, StockMovementFrm
    Holds (model layer): tblStaffMember, tblStockLevel
    """

    staff: tblStaffMember
    list_stock_level: list[tblStockLevel]
    cbo_stock_location: ttk.Combobox
    txt_keyword: ttk.Entry
    chk_below_reorder_point: ttk.Checkbutton
    btn_search: ttk.Button
    tbl_stock_level: ttk.Treeview
    btn_adjust: ttk.Button
    btn_history: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.stock_level_dao = StockLevelDAO()
        self.stock_location_dao = StockLocationDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_adjust(self):
        raise NotImplementedError

    def on_history(self):
        raise NotImplementedError
