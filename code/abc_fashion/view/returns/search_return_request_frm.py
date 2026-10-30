"""SearchReturnRequestFrm — Danh sách yêu cầu trả hàng (UC18)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.return_controller import ReturnController
from abc_fashion.model.returns import ReturnStatus, ReturnRequest
from abc_fashion.model.user import StaffRole, StaffMember
from abc_fashion.view._util import (ChoiceBox, body, enum_choices, fill_table, fmt_dt, guarded, label, make_table, modal,
                                    selected, warn)
from abc_fashion.view.returns.inspect_return_frm import InspectReturnFrm
from abc_fashion.view.returns.process_return_frm import ProcessReturnFrm


class SearchReturnRequestFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_return_request: list[ReturnRequest] = []
        self.return_controller = ReturnController()
        self._build()
        if staff.role == StaffRole.WAREHOUSE:
            self.cbo_status.select_value(ReturnStatus.IN_TRANSIT)
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Yêu cầu trả / đổi hàng")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.txt_keyword = ttk.Entry(bar, width=26)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.cbo_status = ChoiceBox(bar, enum_choices(ReturnStatus, "Mọi trạng thái"), width=16)
        self.cbo_status.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_return_request = make_table(f, [("no", "Mã yêu cầu", 130), ("order", "Mã đơn", 120),
                                                 ("cust", "Khách", 150), ("type", "Loại", 80), ("reason", "Lý do", 120),
                                                 ("date", "Ngày gửi", 120), ("status", "Trạng thái", 110)], height=14)
        self.tbl_return_request.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_return_request.bind("<Double-1>", lambda e: self.on_open())
        text = "Kiểm tra hàng" if self.staff.role == StaffRole.WAREHOUSE else "Xử lý"
        ttk.Button(f, text=text, command=self.on_open).grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_return_request = self.return_controller.search_return_request(self.txt_keyword.get(),
                                                                                self.cbo_status.value())
        fill_table(self.tbl_return_request, [(r.id, (r.return_no, getattr(r, "order_no", ""),
                                                     getattr(r, "customer_name", ""), label(r.return_type),
                                                     label(r.reason_code), fmt_dt(r.requested_at), label(r.status)),
                                              ("mark",) if r.status == ReturnStatus.REQUESTED else ())
                                             for r in self.list_return_request])

    @guarded
    def on_open(self) -> None:
        r = selected(self.tbl_return_request, self.list_return_request)
        if r is None:
            return warn(self, "Chọn một yêu cầu")
        if self.staff.role == StaffRole.WAREHOUSE:
            if r.status != ReturnStatus.IN_TRANSIT:
                return warn(self, "Kho chỉ kiểm tra các yêu cầu đang gửi hàng về")
            modal(InspectReturnFrm(self.staff, r), self)
        else:
            modal(ProcessReturnFrm(self.staff, r), self)
        self.on_search()
