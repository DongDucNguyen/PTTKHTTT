"""SalesReportFrm — Báo cáo doanh số theo style."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import filedialog, ttk

from abc_fashion.controller.report_controller import ReportController
from abc_fashion.model.stat import StyleStat
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, DateEntry, body, fill_table, guarded, info, make_table, money, selected,
                                    warn)
from abc_fashion.view.report.sales_detail_frm import SalesDetailFrm


class SalesReportFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_style_stat: list[StyleStat] = []
        self.report_controller = ReportController()
        self._build()
        today = date.today()
        self.dte_from.set_date(today.replace(day=1))
        self.dte_to.set_date(today)
        self.cbo_category.set_choices([("Mọi danh mục", None)] + [(c.name, c) for c in
                                                                 self.report_controller.get_categories()])
        self.cbo_collection.set_choices([("Mọi bộ sưu tập", None)]
                                        + [(c.name, c) for c in self.report_controller.get_collections()])
        self.on_view()

    def _build(self) -> None:
        f = body(self, "Báo cáo doanh số theo sản phẩm")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        ttk.Label(bar, text="Từ").pack(side="left")
        self.dte_from = DateEntry(bar)
        self.dte_from.pack(side="left", padx=3)
        ttk.Label(bar, text="đến").pack(side="left")
        self.dte_to = DateEntry(bar)
        self.dte_to.pack(side="left", padx=3)
        self.cbo_category = ChoiceBox(bar, width=16)
        self.cbo_category.pack(side="left", padx=3)
        self.cbo_collection = ChoiceBox(bar, width=16)
        self.cbo_collection.pack(side="left", padx=3)
        self.btn_view = ttk.Button(bar, text="Xem", command=self.on_view)
        self.btn_view.pack(side="left", padx=3)
        self.btn_export = ttk.Button(bar, text="Xuất CSV", command=self.on_export)
        self.btn_export.pack(side="left")
        self.tbl_style_stat = make_table(f, [("code", "Mã", 90), ("name", "Sản phẩm", 240), ("qty", "SL bán", 70),
                                             ("rev", "Doanh thu tiền", 120), ("orders", "Số đơn", 70)], height=16)
        self.tbl_style_stat.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_style_stat.bind("<Double-1>", lambda e: self.on_open_detail())
        self.lbl_total_revenue = ttk.Label(f, style="H3.TLabel")
        self.lbl_total_revenue.grid(row=2, column=0, sticky="w")
        ttk.Button(f, text="Xem chi tiết", command=self.on_open_detail).grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    def _period(self):
        return self.dte_from.get_date(), self.dte_to.get_date()

    @guarded
    def on_view(self) -> None:
        self.list_style_stat = self.report_controller.get_sales_report(*self._period(), self.cbo_category.value(),
                                                                       self.cbo_collection.value())
        fill_table(self.tbl_style_stat, [(s.id, (s.code, s.name, s.quantity_sold, money(s.revenue), s.order_count))
                                         for s in self.list_style_stat])
        self.lbl_total_revenue.config(text=f"Tổng doanh thu: {money(sum(s.revenue for s in self.list_style_stat))}")

    @guarded
    def on_open_detail(self) -> None:
        s = selected(self.tbl_style_stat, self.list_style_stat)
        if s is None:
            return warn(self, "Chọn một sản phẩm")
        SalesDetailFrm(s, *self._period())

    @guarded
    def on_export(self) -> None:
        if not self.list_style_stat:
            return warn(self, "Không có dữ liệu để xuất")
        start, end = self._period()
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile=f"doanh_so_{start:%Y%m%d}_{end:%Y%m%d}.csv")
        if not path:
            return
        n = self.report_controller.export_sales_csv(self.list_style_stat, path)
        info(self, f"Đã xuất {n} dòng ra {path}")
