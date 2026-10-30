"""SelectReportFrm — Chọn loại báo cáo (UC16, UC24)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import ChoiceBox, body, guarded
from abc_fashion.view.inventory.stock_level_frm import StockLevelFrm
from abc_fashion.view.report.return_report_frm import ReturnReportFrm
from abc_fashion.view.report.sales_report_frm import SalesReportFrm

REPORTS = [("Doanh số theo sản phẩm", "sales"), ("Trả hàng theo sản phẩm", "returns"), ("Hàng sắp hết", "low_stock")]


class SelectReportFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        f = body(self, "Báo cáo", padding=16)
        ttk.Label(f, text="Loại báo cáo").grid(row=0, column=0, sticky="w")
        self.cbo_report_type = ChoiceBox(f, REPORTS, width=28)
        self.cbo_report_type.grid(row=0, column=1, padx=6)
        self.btn_select = ttk.Button(f, text="Xem", command=self.on_select)
        self.btn_select.grid(row=0, column=2)
        self.resizable(False, False)

    @guarded
    def on_select(self) -> None:
        kind = self.cbo_report_type.value()
        if kind == "sales":
            SalesReportFrm(self.staff)
        elif kind == "returns":
            ReturnReportFrm(self.staff)
        elif kind == "low_stock":
            frm = StockLevelFrm(self.staff)
            frm.var_below_reorder_point.set(True)
            frm.on_search()
