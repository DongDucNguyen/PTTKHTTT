# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.edit_restock_request_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.restock_request_dao import RestockRequestDAO
from abc_fashion.control.dao.stock_location_dao import StockLocationDAO
from abc_fashion.control.dao.supplier_dao import SupplierDAO
from abc_fashion.model.inventory import tblRestockRequest, tblStockLocation
from abc_fashion.model.user import tblStaffMember, tblSupplier


class EditRestockRequestFrm(tk.Toplevel):
    """EditRestockRequestFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): RestockRequestDAO, SupplierDAO, StockLocationDAO
    Opens (view layer): SelectVariantFrm
    Holds (model layer): tblRestockRequest, tblStaffMember, tblStockLocation, tblSupplier
    """

    staff: tblStaffMember
    restock_request: tblRestockRequest
    list_supplier: list[tblSupplier]
    list_stock_location: list[tblStockLocation]
    lbl_request_no: ttk.Label
    cbo_supplier: ttk.Combobox
    cbo_stock_location: ttk.Combobox
    dte_expected_date: DateEntry
    tbl_restock_item: ttk.Treeview
    spn_quantity: ttk.Spinbox
    btn_add_item: ttk.Button
    btn_remove_item: ttk.Button
    btn_save_draft: ttk.Button
    btn_send: ttk.Button

    def __init__(self, staff: tblStaffMember, restock_request: tblRestockRequest | None):
        super().__init__()
        self.staff = staff
        self.restock_request = restock_request
        self.restock_request_dao = RestockRequestDAO()
        self.supplier_dao = SupplierDAO()
        self.stock_location_dao = StockLocationDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_add_item(self):
        raise NotImplementedError

    def on_remove_item(self):
        raise NotImplementedError

    def on_save_draft(self):
        raise NotImplementedError

    def on_send(self):
        raise NotImplementedError
