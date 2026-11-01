# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.stock_movement_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.stock_movement_dao import StockMovementDAO
from abc_fashion.model.catalogue import tblProductVariant
from abc_fashion.model.inventory import tblStockMovement


class StockMovementFrm(tk.Toplevel):
    """StockMovementFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): StockMovementDAO
    Holds (model layer): tblProductVariant, tblStockMovement
    """

    variant: tblProductVariant
    list_movement: list[tblStockMovement]
    dte_from: DateEntry
    dte_to: DateEntry
    cbo_reason: ttk.Combobox
    btn_view: ttk.Button
    tbl_movement: ttk.Treeview

    def __init__(self, variant: tblProductVariant):
        super().__init__()
        self.variant = variant
        self.stock_movement_dao = StockMovementDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_view(self):
        raise NotImplementedError
