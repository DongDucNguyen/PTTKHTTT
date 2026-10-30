"""SalesDetailFrm — Chi tiết các dòng đơn của một style."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk

from abc_fashion.controller.report_controller import ReportController
from abc_fashion.model.sales import OrderItem
from abc_fashion.model.stat import StyleStat
from abc_fashion.view._util import body, fill_table, fmt_dt, make_table, money


class SalesDetailFrm(tk.Toplevel):
    def __init__(self, style_stat: StyleStat, start: date, end: date):
        super().__init__()
        self.style_stat = style_stat
        self.report_controller = ReportController()
        self.list_order_item: list[OrderItem] = self.report_controller.get_sales_detail(style_stat, start, end)
        f = body(self, f"Chi tiết doanh số — {style_stat.code}")
        self.lbl_style_name = ttk.Label(f, text=f"{style_stat.code} – {style_stat.name}", style="H2.TLabel")
        self.lbl_style_name.grid(row=0, column=0, sticky="w")
        self.lbl_period = ttk.Label(f, text=f"Từ {fmt_dt(start)} đến {fmt_dt(end)} · {style_stat.quantity_sold} sản phẩm · "
                                            f"{money(style_stat.revenue)}")
        self.lbl_period.grid(row=1, column=0, sticky="w")
        self.tbl_order_item = make_table(f, [("no", "Mã đơn", 120), ("date", "Ngày", 120), ("sku", "SKU", 110),
                                             ("qty", "SL", 40), ("price", "Đơn giá", 90), ("disc", "Giảm", 80),
                                             ("total", "Thành tiền", 100)], height=14)
        self.tbl_order_item.box.grid(row=2, column=0, sticky="nsew", pady=8)
        fill_table(self.tbl_order_item, [(i.id, (i.order_no, fmt_dt(i.placed_at), i.sku, i.quantity, money(i.unit_price),
                                                 money(i.discount), money(i.line_total))) for i in self.list_order_item])
        f.rowconfigure(2, weight=1)
        f.columnconfigure(0, weight=1)
