"""AuditLogFrm — Xem nhật ký thay đổi (UC20)."""
from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from abc_fashion.controller.account_admin_controller import AccountAdminController
from abc_fashion.model.audit import AuditAction, AuditLogEntry
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, DateEntry, body, enum_choices, fill_table, fmt_dt, guarded, label,
                                    make_table)


class AuditLogFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_entry: list[AuditLogEntry] = []
        self.account_admin_controller = AccountAdminController()
        self._build()
        self.dte_from.set_date(date.today() - timedelta(days=7))
        self.dte_to.set_date(date.today())
        self.cbo_staff.set_choices([("Tất cả", None)] + [(s.full_name, s) for s in
                                                         self.account_admin_controller.get_all_staff()])
        self.on_view()

    def _build(self) -> None:
        f = body(self, "Nhật ký thay đổi")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        ttk.Label(bar, text="Từ").pack(side="left")
        self.dte_from = DateEntry(bar)
        self.dte_from.pack(side="left", padx=4)
        ttk.Label(bar, text="đến").pack(side="left")
        self.dte_to = DateEntry(bar)
        self.dte_to.pack(side="left", padx=4)
        ttk.Label(bar, text="Nhân viên").pack(side="left", padx=(8, 0))
        self.cbo_staff = ChoiceBox(bar, width=20)
        self.cbo_staff.pack(side="left", padx=4)
        ttk.Label(bar, text="Hành động").pack(side="left")
        self.cbo_action = ChoiceBox(bar, enum_choices(AuditAction, "Tất cả"), width=16)
        self.cbo_action.pack(side="left", padx=4)
        self.btn_view = ttk.Button(bar, text="Xem", command=self.on_view)
        self.btn_view.pack(side="left", padx=4)
        self.tbl_audit_log = make_table(f, [("time", "Thời điểm", 130), ("staff", "Nhân viên", 140),
                                            ("entity", "Đối tượng", 130), ("action", "Hành động", 110),
                                            ("changes", "Thay đổi", 360)], height=16)
        self.tbl_audit_log.box.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_view(self) -> None:
        self.list_entry = self.account_admin_controller.search_audit_log(
            self.dte_from.get_date(), self.dte_to.get_date(), self.cbo_staff.value(), self.cbo_action.value())
        fill_table(self.tbl_audit_log, [(e.id, (fmt_dt(e.created_at), getattr(e, "staff_name", ""), e.entity,
                                                label(e.action), e.changes or "")) for e in self.list_entry])
