# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.warehouse_home_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import tblStaffMember


class WarehouseHomeFrm(tk.Toplevel):
    """WarehouseHomeFrm -- layer abc_fashion.view.inventory.
    Opens (view layer): StockLevelFrm, ManageRestockFrm, SearchReturnRequestFrm
    Holds (model layer): tblStaffMember
    """

    staff: tblStaffMember
    btn_view_stock: ttk.Button
    btn_restock: ttk.Button
    btn_inspect_return: ttk.Button
    btn_logout: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        raise NotImplementedError  # create and place the ttk widgets

    def on_view_stock(self):
        raise NotImplementedError

    def on_restock(self):
        raise NotImplementedError

    def on_inspect_return(self):
        raise NotImplementedError

    def on_logout(self):
        raise NotImplementedError
