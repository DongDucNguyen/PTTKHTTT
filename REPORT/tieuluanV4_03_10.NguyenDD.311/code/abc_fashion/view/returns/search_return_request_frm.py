# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.returns.search_return_request_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.model.returns import tblReturnRequest
from abc_fashion.model.user import tblStaffMember


class SearchReturnRequestFrm(tk.Toplevel):
    """SearchReturnRequestFrm -- layer abc_fashion.view.returns.
    Uses (control layer): ReturnRequestDAO
    Opens (view layer): ProcessReturnFrm, InspectReturnFrm
    Holds (model layer): tblReturnRequest, tblStaffMember
    """

    staff: tblStaffMember
    list_return_request: list[tblReturnRequest]
    txt_keyword: ttk.Entry
    cbo_status: ttk.Combobox
    btn_search: ttk.Button
    tbl_return_request: ttk.Treeview

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.return_request_dao = ReturnRequestDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_search(self):
        raise NotImplementedError

    def on_open(self):
        raise NotImplementedError
