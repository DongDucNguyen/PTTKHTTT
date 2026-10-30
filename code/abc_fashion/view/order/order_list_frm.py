"""OrderListFrm — Danh sách đơn của khách (UC09)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.order_controller import OrderController
from abc_fashion.model.sales import OrderStatus, Order
from abc_fashion.model.user import Customer
from abc_fashion.view._util import (ChoiceBox, body, enum_choices, fill_table, fmt_dt, guarded, label, make_table, modal,
                                    money, selected, warn)
from abc_fashion.view.order.order_detail_frm import OrderDetailFrm


class OrderListFrm(tk.Toplevel):
    def __init__(self, customer: Customer):
        super().__init__()
        self.customer = customer
        self.list_order: list[Order] = []
        self.order_controller = OrderController()
        self._build()
        self.on_filter()

    def _build(self) -> None:
        f = body(self, "Đơn hàng của tôi")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        ttk.Label(bar, text="Trạng thái").pack(side="left")
        self.cbo_status = ChoiceBox(bar, enum_choices(OrderStatus, "Tất cả"), width=18)
        self.cbo_status.pack(side="left", padx=4)
        self.btn_filter = ttk.Button(bar, text="Lọc", command=self.on_filter)
        self.btn_filter.pack(side="left")
        self.tbl_order = make_table(f, [("no", "Mã đơn", 130), ("date", "Ngày đặt", 130), ("items", "Số dòng", 70),
                                        ("status", "Trạng thái", 130), ("total", "Tổng tiền", 110)], height=14)
        self.tbl_order.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_order.bind("<Double-1>", lambda e: self.on_open_order())
        ttk.Button(f, text="Xem chi tiết", command=self.on_open_order).grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_filter(self) -> None:
        self.list_order = self.order_controller.get_orders(self.customer, self.cbo_status.value())
        fill_table(self.tbl_order, [(o.id, (o.order_no, fmt_dt(o.placed_at), getattr(o, "item_count", ""),
                                            label(o.status), money(o.grand_total))) for o in self.list_order])

    @guarded
    def on_open_order(self) -> None:
        o = selected(self.tbl_order, self.list_order)
        if o is None:
            return warn(self, "Chọn một đơn hàng")
        modal(OrderDetailFrm(self.customer, o), self)
        self.on_filter()
