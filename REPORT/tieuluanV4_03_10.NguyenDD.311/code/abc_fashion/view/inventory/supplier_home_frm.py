# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.supplier_home_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.restock_request_dao import RestockRequestDAO
from abc_fashion.model.inventory import tblRestockRequest
from abc_fashion.model.user import tblSupplier


class SupplierHomeFrm(tk.Toplevel):
    """SupplierHomeFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): RestockRequestDAO
    Opens (view layer): ConfirmRestockFrm
    Holds (model layer): tblRestockRequest, tblSupplier
    """

    supplier: tblSupplier
    list_restock_request: list[tblRestockRequest]
    cbo_status: ttk.Combobox
    tbl_restock_request: ttk.Treeview
    btn_open: ttk.Button
    btn_logout: ttk.Button

    def __init__(self, supplier: tblSupplier):
        super().__init__()
        self.supplier = supplier
        self.restock_request_dao = RestockRequestDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_open(self):
        raise NotImplementedError

    def on_logout(self):
        raise NotImplementedError
