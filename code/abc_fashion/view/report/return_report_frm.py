"""ReturnReportFrm — Báo cáo trả hàng theo style."""
from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from abc_fashion.controller.report_controller import ReportController
from abc_fashion.model.returns import ReturnReason
from abc_fashion.model.stat import ReturnStat
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, DateEntry, body, enum_choices, fill_table, guarded, label, make_table,
                                    selected, warn)
from abc_fashion.view.report.return_detail_frm import ReturnDetailFrm


class ReturnReportFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_return_stat: list[ReturnStat] = []
        self.report_controller = ReportController()
        self._build()
        self.dte_from.set_date(date.today() - timedelta(days=90))
        self.dte_to.set_date(date.today())
        self.on_view()

    def _build(self) -> None:
        f = body(self, "Báo cáo trả hàng theo sản phẩm")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        ttk.Label(bar, text="Từ").pack(side="left")
        self.dte_from = DateEntry(bar)
        self.dte_from.pack(side="left", padx=3)
        ttk.Label(bar, text="đến").pack(side="left")
        self.dte_to = DateEntry(bar)
        self.dte_to.pack(side="left", padx=3)
        self.cbo_reason = ChoiceBox(bar, enum_choices(ReturnReason, "Mọi lý do"), width=18)
        self.cbo_reason.pack(side="left", padx=3)
        self.btn_view = ttk.Button(bar, text="Xem", command=self.on_view)
        self.btn_view.pack(side="left", padx=3)
        self.tbl_return_stat = make_table(f, [("code", "Mã", 90), ("name", "Sản phẩm", 230), ("sold", "SL bán", 70),
                                              ("ret", "SL trả", 70), ("rate", "Tỉ lệ trả", 80),
                                              ("reason", "Lý do chính", 130)], height=16)
        self.tbl_return_stat.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_return_stat.bind("<Double-1>", lambda e: self.on_open_detail())
        ttk.Button(f, text="Xem chi tiết", command=self.on_open_detail).grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_view(self) -> None:
        self.list_return_stat = self.report_controller.get_return_report(self.dte_from.get_date(),
                                                                         self.dte_to.get_date(), self.cbo_reason.value())
        fill_table(self.tbl_return_stat, [(s.id, (s.code, s.name, s.quantity_sold, s.quantity_returned,
                                                  f"{s.return_rate * 100:.1f}%" if s.return_rate is not None else "—",
                                                  label(s.main_reason))) for s in self.list_return_stat])

    @guarded
    def on_open_detail(self) -> None:
        s = selected(self.tbl_return_stat, self.list_return_stat)
        if s is None:
            return warn(self, "Chọn một sản phẩm")
        ReturnDetailFrm(s, self.dte_from.get_date(), self.dte_to.get_date())
