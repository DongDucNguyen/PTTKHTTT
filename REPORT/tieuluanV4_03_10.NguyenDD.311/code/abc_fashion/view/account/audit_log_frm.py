# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.audit_log_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.audit_log_entry_dao import AuditLogEntryDAO
from abc_fashion.model.audit import tblAuditLogEntry
from abc_fashion.model.user import tblStaffMember


class AuditLogFrm(tk.Toplevel):
    """AuditLogFrm -- layer abc_fashion.view.account.
    Uses (control layer): AuditLogEntryDAO
    Holds (model layer): tblAuditLogEntry, tblStaffMember
    """

    staff: tblStaffMember
    list_entry: list[tblAuditLogEntry]
    dte_from: DateEntry
    dte_to: DateEntry
    cbo_staff: ttk.Combobox
    cbo_action: ttk.Combobox
    btn_view: ttk.Button
    tbl_audit_log: ttk.Treeview

    def __init__(self, staff: tblStaffMember):
        super().__init__()
        self.staff = staff
        self.audit_log_entry_dao = AuditLogEntryDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_view(self):
        raise NotImplementedError
