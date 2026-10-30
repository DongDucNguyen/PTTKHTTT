"""InspectReturnFrm — Kho kiểm tra hàng trả về."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.return_controller import ReturnController
from abc_fashion.model.returns import InspectionResult, ReturnRequest
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, body, confirm, fill_table, guarded, info, label, make_table, message_label,
                                    selected, show)


class InspectReturnFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, return_request: ReturnRequest):
        super().__init__()
        self.staff = staff
        self.return_controller = ReturnController()
        self.return_request = self.return_controller.get_return_request_detail(return_request)
        self._build()
        self._refresh()

    def _build(self) -> None:
        r = self.return_request
        f = body(self, f"Kiểm tra hàng trả — {r.return_no}")
        self.lbl_return_no = ttk.Label(f, text=f"{r.return_no} · đơn {getattr(r, 'order_no', '')} · {label(r.status)}",
                                       style="H3.TLabel")
        self.lbl_return_no.grid(row=0, column=0, columnspan=4, sticky="w")
        self.tbl_return_item = make_table(f, [("sku", "SKU", 110), ("name", "Sản phẩm", 200), ("qty", "SL", 40),
                                              ("result", "Kết quả", 90), ("note", "Ghi chú", 220)], height=6)
        self.tbl_return_item.box.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=6)
        ttk.Label(f, text="Kết quả").grid(row=2, column=0, sticky="w")
        self.cbo_inspection_result = ChoiceBox(f, [(label(InspectionResult.PASSED), InspectionResult.PASSED),
                                                   (label(InspectionResult.FAILED), InspectionResult.FAILED)], width=12)
        self.cbo_inspection_result.grid(row=2, column=1, sticky="w")
        self.txt_inspection_note = ttk.Entry(f, width=40)
        self.txt_inspection_note.grid(row=2, column=2, sticky="w", padx=4)
        self.btn_save_inspection = ttk.Button(f, text="Lưu dòng", command=self.on_save_inspection)
        self.btn_save_inspection.grid(row=2, column=3)
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=3, column=0, columnspan=4, sticky="w")
        self.btn_finish = ttk.Button(f, text="Hoàn tất kiểm tra", command=self.on_finish)
        self.btn_finish.grid(row=4, column=3, sticky="e", pady=6)
        if not r.can_inspect:
            for w in (self.btn_save_inspection, self.btn_finish):
                w.state(["disabled"])
        f.columnconfigure(2, weight=1)

    def _refresh(self) -> None:
        fill_table(self.tbl_return_item, [(i.id, (i.sku, getattr(i, "style_name", ""), i.quantity,
                                                  label(i.inspection_result), i.inspection_note or ""))
                                          for i in self.return_request.items])

    @guarded
    def on_save_inspection(self) -> None:
        item = selected(self.tbl_return_item, self.return_request.items)
        if item is None:
            return show(self.lbl_message, "Chọn một dòng")
        self.return_controller.save_inspection(item, self.cbo_inspection_result.value(), self.txt_inspection_note.get())
        self.txt_inspection_note.delete(0, "end")
        show(self.lbl_message, "")
        self._refresh()

    @guarded
    def on_finish(self) -> None:
        r = self.return_request
        passed = sum(i.quantity for i in r.items if i.inspection_result == InspectionResult.PASSED)
        if not confirm(self, f"Hoàn tất kiểm tra? {passed} sản phẩm đạt sẽ được nhập lại kho."):
            return
        self.return_controller.finish_inspection(self.staff, r)
        info(self, "Đã hoàn tất kiểm tra")
        self.destroy()
