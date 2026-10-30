"""ConfirmRestockFrm — Nhà cung cấp xác nhận / từ chối phiếu."""
from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

from abc_fashion.controller._errors import AccessDenied
from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.inventory import RestockStatus, RestockRequest
from abc_fashion.model.user import Supplier
from abc_fashion.view._util import (DateEntry, body, confirm, fill_table, guarded, info, label, make_table, message_label,
                                    text_get, text_set)


class ConfirmRestockFrm(tk.Toplevel):
    def __init__(self, supplier: Supplier, restock_request: RestockRequest):
        super().__init__()
        self.supplier = supplier
        self.inventory_controller = InventoryController()
        try:
            self.restock_request = self.inventory_controller.get_supplier_restock(supplier, restock_request)
            denied = None
        except AccessDenied as e:
            self.restock_request, denied = restock_request, e
        self._build()
        if denied is not None:
            messagebox.showerror("Không có quyền", str(denied), parent=self)
            self.after(0, self.destroy)
            return
        r = self.restock_request
        fill_table(self.tbl_restock_item, [(i.id, (i.sku, getattr(i, "style_name", ""), f"{i.colour}/{i.size_label}",
                                                   i.quantity)) for i in r.items])
        self.dte_expected_date.set_date(r.expected_date or date.today() + timedelta(days=7))
        text_set(self.txa_supplier_note, r.supplier_note or "")
        editable = r.status == RestockStatus.SENT
        for w in (self.btn_confirm, self.btn_refuse):
            w.state(["!disabled"] if editable else ["disabled"])

    def _build(self) -> None:
        r = self.restock_request
        f = body(self, f"Phiếu nhập {r.request_no}")
        self.lbl_request_no = ttk.Label(f, text=f"Phiếu {r.request_no} · {label(r.status)}", style="H2.TLabel")
        self.lbl_request_no.grid(row=0, column=0, columnspan=2, sticky="w")
        self.lbl_stock_location = ttk.Label(f, text=f"Giao tới: {getattr(r, 'location_name', '')}")
        self.lbl_stock_location.grid(row=1, column=0, columnspan=2, sticky="w")
        self.tbl_restock_item = make_table(f, [("sku", "SKU", 110), ("name", "Sản phẩm", 200), ("var", "Màu / cỡ", 90),
                                               ("qty", "Số lượng", 70)], height=6)
        self.tbl_restock_item.box.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=6)
        ttk.Label(f, text="Ngày giao dự kiến").grid(row=3, column=0, sticky="w")
        self.dte_expected_date = DateEntry(f)
        self.dte_expected_date.grid(row=3, column=1, sticky="w")
        ttk.Label(f, text="Ghi chú / lý do từ chối").grid(row=4, column=0, sticky="nw", pady=4)
        self.txa_supplier_note = tk.Text(f, height=3, width=46, wrap="word")
        self.txa_supplier_note.grid(row=4, column=1, sticky="we", pady=4)
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=5, column=0, columnspan=2, sticky="w")
        bar = ttk.Frame(f)
        bar.grid(row=6, column=0, columnspan=2, sticky="e")
        self.btn_refuse = ttk.Button(bar, text="Từ chối", command=self.on_refuse)
        self.btn_refuse.pack(side="left", padx=3)
        self.btn_confirm = ttk.Button(bar, text="Xác nhận", command=self.on_confirm)
        self.btn_confirm.pack(side="left")

    @guarded
    def on_confirm(self) -> None:
        self.inventory_controller.confirm_restock(self.supplier, self.restock_request, self.dte_expected_date.get_date(),
                                                  text_get(self.txa_supplier_note))
        info(self, "Đã xác nhận phiếu")
        self.destroy()

    @guarded
    def on_refuse(self) -> None:
        if text_get(self.txa_supplier_note) and not confirm(self, "Từ chối phiếu nhập này?"):
            return
        self.inventory_controller.refuse_restock(self.supplier, self.restock_request, text_get(self.txa_supplier_note))
        self.destroy()
