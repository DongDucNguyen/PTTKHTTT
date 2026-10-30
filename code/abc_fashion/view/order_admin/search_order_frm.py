"""SearchOrderFrm — Tìm đơn (UC22)."""
from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from abc_fashion.controller.order_admin_controller import OrderAdminController
from abc_fashion.model.sales import OrderStatus, Order
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, DateEntry, body, enum_choices, fill_table, fmt_dt, guarded, label,
                                    make_table, modal, money, selected, warn)
from abc_fashion.view.order_admin.manage_order_frm import ManageOrderFrm


class SearchOrderFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_order: list[Order] = []
        self.order_admin_controller = OrderAdminController()
        self._build()
        self.dte_from.set_date(date.today() - timedelta(days=30))
        self.dte_to.set_date(date.today())
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Quản lý đơn hàng")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.txt_keyword = ttk.Entry(bar, width=24)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.cbo_status = ChoiceBox(bar, enum_choices(OrderStatus, "Mọi trạng thái"), width=16)
        self.cbo_status.pack(side="left", padx=4)
        ttk.Label(bar, text="Từ").pack(side="left")
        self.dte_from = DateEntry(bar)
        self.dte_from.pack(side="left", padx=3)
        ttk.Label(bar, text="đến").pack(side="left")
        self.dte_to = DateEntry(bar)
        self.dte_to.pack(side="left", padx=3)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left", padx=4)
        self.tbl_order = make_table(f, [("no", "Mã đơn", 120), ("date", "Ngày đặt", 120), ("cust", "Khách", 150),
                                        ("phone", "Điện thoại", 100), ("status", "Trạng thái", 120),
                                        ("total", "Tổng tiền", 100), ("note", "Yêu cầu huỷ", 160)], height=16)
        self.tbl_order.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_order.bind("<Double-1>", lambda e: self.on_open_order())
        ttk.Button(f, text="Xử lý đơn", command=self.on_open_order).grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_order = self.order_admin_controller.search_order(self.txt_keyword.get(), self.cbo_status.value(),
                                                                   self.dte_from.get_date(), self.dte_to.get_date())
        fill_table(self.tbl_order, [(o.id, (o.order_no, fmt_dt(o.placed_at), getattr(o, "customer_name", ""),
                                            getattr(o, "customer_phone", ""), label(o.status), money(o.grand_total),
                                            o.cancel_reason if getattr(o, "cancel_requested", False) else ""),
                                     ("mark",) if getattr(o, "cancel_requested", False) else ())
                                    for o in self.list_order])

    @guarded
    def on_open_order(self) -> None:
        o = selected(self.tbl_order, self.list_order)
        if o is None:
            return warn(self, "Chọn một đơn")
        modal(ManageOrderFrm(self.staff, o), self)
        self.on_search()
