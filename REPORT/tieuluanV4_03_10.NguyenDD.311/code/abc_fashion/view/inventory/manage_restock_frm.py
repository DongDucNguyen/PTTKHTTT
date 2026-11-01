# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.manage_restock_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.restock_request_dao import RestockRequestDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.stock_movement_dao import StockMovementDAO
from abc_fashion.model.inventory import tblRestockRequest
from abc_fashion.model.user import tblStaffMember


class ManageRestockFrm(tk.Toplevel):
    """ManageRestockFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): RestockRequestDAO, StockLevelDAO, StockMovementDAO
    Opens (view layer): EditRestockRequestFrm
    Holds (model layer): tblRestockRequest, tblStaffMember
    """

    staff: tblStaffMember
    list_restock_request: list[tblRestockRequest]
    cbo_status: ttk.Combobox
    cbo_supplier: ttk.Combobox
    btn_search: ttk.Button
    tbl_restock_request: ttk.Treeview
    btn_create: ttk.Button
    btn_open: ttk.Button
    btn_mark_received: ttk.Button

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.restock_request_dao = RestockRequestDAO()
        self.stock_level_dao = StockLevelDAO()
        self.stock_movement_dao = StockMovementDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_create(self):
        raise NotImplementedError

    def on_open(self):
        raise NotImplementedError

    def on_mark_received(self):
        raise NotImplementedError
