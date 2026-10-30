"""SupplierHomeFrm — Trang chủ nhà cung cấp: các phiếu được gửi tới họ."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.inventory import RestockStatus, RestockRequest
from abc_fashion.model.user import Supplier
from abc_fashion.view._util import (ChoiceBox, body, fill_table, fmt_dt, guarded, label, logout, make_table, modal,
                                    selected, warn)
from abc_fashion.view.inventory.confirm_restock_frm import ConfirmRestockFrm


class SupplierHomeFrm(tk.Toplevel):
    def __init__(self, supplier: Supplier):
        super().__init__()
        self.supplier = supplier
        self.list_restock_request: list[RestockRequest] = []
        self.inventory_controller = InventoryController()
        self._build()
        self._reload()

    def _build(self) -> None:
        f = body(self, f"Nhà cung cấp — {self.supplier.name}")
        ttk.Label(f, text=f"Xin chào {self.supplier.name}", style="H2.TLabel").grid(row=0, column=0, sticky="w")
        bar = ttk.Frame(f)
        bar.grid(row=1, column=0, sticky="w", pady=6)
        ttk.Label(bar, text="Trạng thái").pack(side="left")
        self.cbo_status = ChoiceBox(bar, [("Chờ xác nhận", RestockStatus.SENT), ("Tất cả", None)]
                                    + [(label(s), s) for s in RestockStatus if s not in (RestockStatus.DRAFT, RestockStatus.SENT)],
                                    width=16)
        self.cbo_status.pack(side="left", padx=4)
        self.cbo_status.bind("<<ComboboxSelected>>", lambda e: self._reload())
        self.tbl_restock_request = make_table(f, [("no", "Số phiếu", 130), ("date", "Ngày lập", 120),
                                                  ("loc", "Kho nhận", 120), ("items", "Số dòng", 60), ("qty", "Tổng SL", 70),
                                                  ("expected", "Ngày giao dự kiến", 120), ("status", "Trạng thái", 110)],
                                              height=12)
        self.tbl_restock_request.box.grid(row=2, column=0, sticky="nsew")
        self.tbl_restock_request.bind("<Double-1>", lambda e: self.on_open())
        bar2 = ttk.Frame(f)
        bar2.grid(row=3, column=0, sticky="e", pady=6)
        self.btn_open = ttk.Button(bar2, text="Mở phiếu", command=self.on_open)
        self.btn_open.pack(side="left", padx=3)
        self.btn_logout = ttk.Button(bar2, text="Đăng xuất", command=self.on_logout)
        self.btn_logout.pack(side="left")
        f.rowconfigure(2, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def _reload(self) -> None:
        self.list_restock_request = self.inventory_controller.search_restock_request(self.cbo_status.value(),
                                                                                     self.supplier)
        fill_table(self.tbl_restock_request, [(r.id, (r.request_no, fmt_dt(r.created_at), getattr(r, "location_name", ""),
                                                      getattr(r, "item_count", ""), getattr(r, "total_qty", ""),
                                                      fmt_dt(r.expected_date), label(r.status)))
                                              for r in self.list_restock_request])

    @guarded
    def on_open(self) -> None:
        r = selected(self.tbl_restock_request, self.list_restock_request)
        if r is None:
            return warn(self, "Chọn một phiếu")
        modal(ConfirmRestockFrm(self.supplier, r), self)
        self._reload()

    def on_logout(self) -> None:
        logout(self)
