# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.inventory.confirm_restock_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.restock_request_dao import RestockRequestDAO
from abc_fashion.model.inventory import tblRestockRequest
from abc_fashion.model.user import tblSupplier


class ConfirmRestockFrm(tk.Toplevel):
    """ConfirmRestockFrm -- layer abc_fashion.view.inventory.
    Uses (control layer): RestockRequestDAO
    Holds (model layer): tblRestockRequest, tblSupplier
    """

    supplier: tblSupplier
    restock_request: tblRestockRequest
    lbl_request_no: ttk.Label
    lbl_stock_location: ttk.Label
    tbl_restock_item: ttk.Treeview
    dte_expected_date: DateEntry
    txa_supplier_note: tk.Text
    btn_confirm: ttk.Button
    btn_refuse: ttk.Button

    def __init__(self, supplier: tblSupplier, restock_request: tblRestockRequest):
        super().__init__()
        self.supplier = supplier
        self.restock_request = restock_request
        self.restock_request_dao = RestockRequestDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_confirm(self):
        raise NotImplementedError

    def on_refuse(self):
        raise NotImplementedError
