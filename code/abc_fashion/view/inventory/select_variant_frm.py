"""SelectVariantFrm — Chọn một biến thể (dùng ở phiếu nhập hàng). Kết quả ở `selected`."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.catalogue import ProductVariant
from abc_fashion.view._util import body, fill_table, guarded, label, make_table, money, selected, warn


class SelectVariantFrm(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.inventory_controller = InventoryController()
        self.list_variant: list[ProductVariant] = []
        self.selected: ProductVariant | None = None
        f = body(self, "Chọn biến thể")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.txt_keyword = ttk.Entry(bar, width=28)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left", padx=4)
        self.tbl_variant = make_table(f, [("sku", "SKU", 110), ("name", "Sản phẩm", 200), ("var", "Màu / cỡ", 90),
                                          ("price", "Giá", 90), ("loc", "Kho", 110), ("status", "Trạng thái", 80)], height=12)
        self.tbl_variant.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_variant.bind("<Double-1>", lambda e: self.on_select())
        self.btn_select = ttk.Button(f, text="Chọn", command=self.on_select)
        self.btn_select.grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)
        self.on_search()

    @guarded
    def on_search(self) -> None:
        self.list_variant = self.inventory_controller.search_variant(self.txt_keyword.get())
        fill_table(self.tbl_variant, [(v.id, (v.sku, getattr(v, "style_name", ""), f"{v.colour}/{v.size_label}",
                                              money(v.price), getattr(v, "location_name", "") or "", label(v.status)))
                                      for v in self.list_variant])

    def on_select(self) -> None:
        self.selected = selected(self.tbl_variant, self.list_variant)
        if self.selected is None:
            return warn(self, "Chọn một biến thể")
        self.destroy()
