"""ReturnDetailFrm — Chi tiết các dòng trả của một style."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk

from abc_fashion.controller.report_controller import ReportController
from abc_fashion.model.returns import ReturnReason, ReturnItem
from abc_fashion.model.stat import ReturnStat
from abc_fashion.view._util import body, fill_table, fmt_dt, label, make_table


class ReturnDetailFrm(tk.Toplevel):
    def __init__(self, return_stat: ReturnStat, start: date, end: date):
        super().__init__()
        self.return_stat = return_stat
        self.report_controller = ReportController()
        self.list_return_item: list[ReturnItem] = self.report_controller.get_return_detail(return_stat, start, end)
        f = body(self, f"Chi tiết trả hàng — {return_stat.code}")
        self.lbl_style_name = ttk.Label(f, text=f"{return_stat.code} – {return_stat.name} · {fmt_dt(start)} – {fmt_dt(end)}",
                                        style="H2.TLabel")
        self.lbl_style_name.grid(row=0, column=0, sticky="w")
        self.tbl_return_item = make_table(f, [("no", "Mã trả", 120), ("order", "Mã đơn", 120), ("date", "Ngày", 110),
                                              ("sku", "SKU", 110), ("qty", "SL", 40), ("reason", "Lý do", 120),
                                              ("result", "Kiểm tra", 80), ("note", "Ghi chú", 180)], height=14)
        self.tbl_return_item.box.grid(row=1, column=0, sticky="nsew", pady=8)
        fill_table(self.tbl_return_item, [(i.id, (i.return_no, i.order_no, fmt_dt(i.requested_at), i.sku, i.quantity,
                                                  label(ReturnReason(i.reason_code)), label(i.inspection_result),
                                                  i.inspection_note or "")) for i in self.list_return_item])
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)
