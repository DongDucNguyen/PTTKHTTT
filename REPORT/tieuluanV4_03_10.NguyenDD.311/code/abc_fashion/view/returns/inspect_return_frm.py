# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.returns.inspect_return_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.stock_movement_dao import StockMovementDAO
from abc_fashion.model.returns import tblReturnRequest
from abc_fashion.model.user import tblStaffMember


class InspectReturnFrm(tk.Toplevel):
    """InspectReturnFrm -- layer abc_fashion.view.returns.
    Uses (control layer): ReturnRequestDAO, StockLevelDAO, StockMovementDAO
    Holds (model layer): tblReturnRequest, tblStaffMember
    """

    staff: tblStaffMember
    return_request: tblReturnRequest
    lbl_return_no: ttk.Label
    tbl_return_item: ttk.Treeview
    cbo_inspection_result: ttk.Combobox
    txt_inspection_note: ttk.Entry
    btn_save_inspection: ttk.Button
    btn_finish: ttk.Button

    def __init__(self, staff: tblStaffMember, return_request: tblReturnRequest):
        super().__init__()
        self.staff = staff
        self.return_request = return_request
        self.return_request_dao = ReturnRequestDAO()
        self.stock_level_dao = StockLevelDAO()
        self.stock_movement_dao = StockMovementDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_save_inspection(self):
        raise NotImplementedError

    def on_finish(self):
        raise NotImplementedError
