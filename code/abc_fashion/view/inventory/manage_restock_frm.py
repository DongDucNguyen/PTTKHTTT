"""ManageRestockFrm — Danh sách phiếu nhập hàng (UC17)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.inventory import RestockStatus, RestockRequest
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, body, confirm, enum_choices, fill_table, fmt_dt, guarded, info, label,
                                    make_table, modal, selected, warn)
from abc_fashion.view.inventory.edit_restock_request_frm import EditRestockRequestFrm


class ManageRestockFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_restock_request: list[RestockRequest] = []
        self.inventory_controller = InventoryController()
        self._build()
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Phiếu nhập hàng")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.cbo_status = ChoiceBox(bar, enum_choices(RestockStatus, "Mọi trạng thái"), width=16)
        self.cbo_status.pack(side="left")
        self.cbo_supplier = ChoiceBox(bar, [("Mọi nhà cung cấp", None)] + [(s.name, s) for s in
                                                                          self.inventory_controller.get_suppliers()], width=24)
        self.cbo_supplier.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_restock_request = make_table(f, [("no", "Số phiếu", 130), ("date", "Ngày lập", 120),
                                                  ("sup", "Nhà cung cấp", 170), ("loc", "Kho", 110), ("qty", "Tổng SL", 70),
                                                  ("expected", "Dự kiến", 90), ("status", "Trạng thái", 110)], height=14)
        self.tbl_restock_request.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_restock_request.bind("<Double-1>", lambda e: self.on_open())
        bar2 = ttk.Frame(f)
        bar2.grid(row=2, column=0, sticky="e")
        self.btn_create = ttk.Button(bar2, text="Lập phiếu", command=self.on_create)
        self.btn_open = ttk.Button(bar2, text="Mở / sửa", command=self.on_open)
        self.btn_mark_received = ttk.Button(bar2, text="Đã nhận hàng", command=self.on_mark_received)
        for b in (self.btn_create, self.btn_open, self.btn_mark_received):
            b.pack(side="left", padx=3)
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_restock_request = self.inventory_controller.search_restock_request(self.cbo_status.value(),
                                                                                     self.cbo_supplier.value())
        fill_table(self.tbl_restock_request, [(r.id, (r.request_no, fmt_dt(r.created_at), getattr(r, "supplier_name", ""),
                                                      getattr(r, "location_name", ""), getattr(r, "total_qty", ""),
                                                      fmt_dt(r.expected_date), label(r.status)),
                                               ("mark",) if r.status == RestockStatus.CONFIRMED else ())
                                              for r in self.list_restock_request])

    @guarded
    def on_create(self) -> None:
        modal(EditRestockRequestFrm(self.staff, None), self)
        self.on_search()

    @guarded
    def on_open(self) -> None:
        r = selected(self.tbl_restock_request, self.list_restock_request)
        if r is None:
            return warn(self, "Chọn một phiếu")
        modal(EditRestockRequestFrm(self.staff, r), self)
        self.on_search()

    @guarded
    def on_mark_received(self) -> None:
        r = selected(self.tbl_restock_request, self.list_restock_request)
        if r is None:
            return warn(self, "Chọn một phiếu")
        if r.status == RestockStatus.CONFIRMED and not confirm(
                self, f"Xác nhận đã nhận đủ hàng của phiếu {r.request_no}? Tồn kho sẽ được cộng."):
            return
        try:
            info(self, f"Đã nhập kho {self.inventory_controller.receive_restock(self.staff, r)} sản phẩm")
        finally:
            self.on_search()
