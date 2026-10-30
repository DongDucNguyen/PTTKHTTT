"""EditRestockRequestFrm — Lập / sửa phiếu nhập hàng."""
from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.inventory import RestockStatus, RestockRequest, StockLocation
from abc_fashion.model.user import StaffMember, Supplier
from abc_fashion.view._util import (ChoiceBox, DateEntry, body, fill_table, guarded, info, label, make_table,
                                    message_label, modal, show)
from abc_fashion.view.inventory.select_variant_frm import SelectVariantFrm


class EditRestockRequestFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, restock_request: RestockRequest | None):
        super().__init__()
        self.staff = staff
        self.inventory_controller = InventoryController()
        self.list_supplier: list[Supplier] = self.inventory_controller.get_suppliers()
        self.list_stock_location: list[StockLocation] = self.inventory_controller.get_stock_locations()
        self.restock_request = self.inventory_controller.get_restock_request_detail(restock_request)
        self._build()
        self._fill()

    def _build(self) -> None:
        f = body(self, "Phiếu nhập hàng")
        self.lbl_request_no = ttk.Label(f, style="H2.TLabel")
        self.lbl_request_no.grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(f, text="Nhà cung cấp").grid(row=1, column=0, sticky="w")
        self.cbo_supplier = ChoiceBox(f, [(s.name, s) for s in self.list_supplier], width=26)
        self.cbo_supplier.grid(row=1, column=1, sticky="w")
        ttk.Label(f, text="Kho nhận").grid(row=1, column=2, sticky="w", padx=(10, 0))
        self.cbo_stock_location = ChoiceBox(f, [(l.name, l) for l in self.list_stock_location], width=18)
        self.cbo_stock_location.grid(row=1, column=3, sticky="w")
        ttk.Label(f, text="Ngày cần hàng").grid(row=2, column=0, sticky="w")
        self.dte_expected_date = DateEntry(f)
        self.dte_expected_date.grid(row=2, column=1, sticky="w", pady=3)
        self.tbl_restock_item = make_table(f, [("sku", "SKU", 110), ("name", "Sản phẩm", 200), ("var", "Màu / cỡ", 90),
                                               ("qty", "Số lượng", 70)], height=8)
        self.tbl_restock_item.box.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=6)
        bar = ttk.Frame(f)
        bar.grid(row=4, column=0, columnspan=4, sticky="w")
        ttk.Label(bar, text="Số lượng").pack(side="left")
        self.spn_quantity = ttk.Spinbox(bar, from_=1, to=10000, width=7)
        self.spn_quantity.set(10)
        self.spn_quantity.pack(side="left", padx=4)
        self.btn_add_item = ttk.Button(bar, text="Thêm biến thể…", command=self.on_add_item)
        self.btn_add_item.pack(side="left", padx=3)
        self.btn_remove_item = ttk.Button(bar, text="Bỏ dòng", command=self.on_remove_item)
        self.btn_remove_item.pack(side="left")
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=5, column=0, columnspan=4, sticky="w")
        bar2 = ttk.Frame(f)
        bar2.grid(row=6, column=0, columnspan=4, sticky="e", pady=4)
        self.btn_save_draft = ttk.Button(bar2, text="Lưu nháp", command=self.on_save_draft)
        self.btn_save_draft.pack(side="left", padx=3)
        self.btn_send = ttk.Button(bar2, text="Gửi nhà cung cấp", command=self.on_send)
        self.btn_send.pack(side="left")
        f.columnconfigure(1, weight=1)

    def _fill(self) -> None:
        r = self.restock_request
        self.lbl_request_no.config(text=f"Phiếu {r.request_no or '(mới)'} · {label(r.status)}"
                                        + (f" · NCC ghi chú: {r.supplier_note}" if r.supplier_note else ""))
        by_id = lambda x: x.id if hasattr(x, "id") else x                                    # noqa: E731
        if r.supplierId:
            self.cbo_supplier.select_value(r.supplierId, key=by_id)
        if r.stockLocationId:
            self.cbo_stock_location.select_value(r.stockLocationId, key=by_id)
        self.dte_expected_date.set_date(r.expected_date or date.today() + timedelta(days=7))
        self._refresh()
        if r.status != RestockStatus.DRAFT:                       # chỉ sửa được phiếu nháp
            for w in (self.cbo_supplier, self.cbo_stock_location, self.btn_add_item, self.btn_remove_item,
                      self.btn_save_draft, self.btn_send):
                w.state(["disabled"])

    def _refresh(self) -> None:
        fill_table(self.tbl_restock_item, [(i.productVariantId, (i.sku, getattr(i, "style_name", ""),
                                                                 f"{i.colour}/{i.size_label}", i.quantity))
                                           for i in self.restock_request.items])

    @guarded
    def on_add_item(self) -> None:
        try:
            qty = int(self.spn_quantity.get())
        except ValueError:
            qty = 0
        if qty <= 0:
            return show(self.lbl_message, "Số lượng phải > 0")
        frm = SelectVariantFrm()
        modal(frm, self)
        if frm.selected is None:
            return
        self.inventory_controller.add_restock_item(self.restock_request, frm.selected, qty,
                                                   self.cbo_stock_location.value())
        show(self.lbl_message, "")
        self._refresh()

    def on_remove_item(self) -> None:
        sel = self.tbl_restock_item.selection()
        if sel:
            self.restock_request.items = [i for i in self.restock_request.items if str(i.productVariantId) != sel[0]]
            self._refresh()

    def _save(self, send: bool) -> None:
        self.inventory_controller.save_restock_request(self.staff, self.restock_request, self.cbo_supplier.value(),
                                                       self.cbo_stock_location.value(),
                                                       self.dte_expected_date.get_date(), send)

    @guarded
    def on_save_draft(self) -> None:
        self._save(False)
        info(self, f"Đã lưu nháp {self.restock_request.request_no}")
        self.destroy()

    @guarded
    def on_send(self) -> None:
        self._save(True)
        info(self, f"Đã gửi phiếu {self.restock_request.request_no} cho {self.cbo_supplier.value().name}")
        self.destroy()
