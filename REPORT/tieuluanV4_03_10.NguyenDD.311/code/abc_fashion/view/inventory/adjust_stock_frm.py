# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.adjust_stock_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.model.inventory import tblStockLevel
from abc_fashion.model.user import tblStaffMember


class AdjustStockFrm(tk.Toplevel):
    """AdjustStockFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): StockLevelDAO
    Holds (model layer): tblStaffMember, tblStockLevel
    """

    staff: tblStaffMember
    stock_level: tblStockLevel
    lbl_sku: ttk.Label
    lbl_stock_location: ttk.Label
    lbl_on_hand: ttk.Label
    lbl_reserved: ttk.Label
    spn_quantity_change: ttk.Spinbox
    txt_reference: ttk.Entry
    txa_note: tk.Text
    btn_save: ttk.Button
    btn_cancel: ttk.Button

    def __init__(self, staff: tblStaffMember, stock_level: tblStockLevel):
        super().__init__()
        self.staff = staff
        self.stock_level = stock_level
        self.stock_level_dao = StockLevelDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_save(self):
        raise NotImplementedError

    def on_cancel(self):
        raise NotImplementedError
