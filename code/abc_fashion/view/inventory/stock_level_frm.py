"""StockLevelFrm — Tồn kho theo kho (UC17), cũng là báo cáo hàng sắp hết."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.catalogue import ProductVariant
from abc_fashion.model.inventory import StockLevel
from abc_fashion.model.user import StaffRole, StaffMember
from abc_fashion.view._util import ChoiceBox, body, fill_table, guarded, make_table, modal, selected, warn
from abc_fashion.view.inventory.adjust_stock_frm import AdjustStockFrm
from abc_fashion.view.inventory.stock_movement_frm import StockMovementFrm


class StockLevelFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_stock_level: list[StockLevel] = []
        self.inventory_controller = InventoryController()
        self._build()
        self.cbo_stock_location.set_choices([("Mọi kho", None)] + [(l.name, l) for l in
                                                                  self.inventory_controller.get_stock_locations()])
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Tồn kho")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.cbo_stock_location = ChoiceBox(bar, width=16)
        self.cbo_stock_location.pack(side="left")
        self.txt_keyword = ttk.Entry(bar, width=24)
        self.txt_keyword.pack(side="left", padx=4)
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.var_below_reorder_point = tk.BooleanVar(value=False)
        self.chk_below_reorder_point = ttk.Checkbutton(bar, text="Chỉ hàng dưới điểm đặt hàng lại",
                                                       variable=self.var_below_reorder_point)
        self.chk_below_reorder_point.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_stock_level = make_table(f, [("sku", "SKU", 110), ("name", "Sản phẩm", 200), ("var", "Màu / cỡ", 90),
                                              ("loc", "Kho", 110), ("on_hand", "Tồn thực", 80),
                                              ("reserved", "Đang giữ", 80), ("available", "Có thể bán", 90),
                                              ("rop", "Điểm đặt lại", 90)], height=16)
        self.tbl_stock_level.box.grid(row=1, column=0, sticky="nsew", pady=8)
        bar2 = ttk.Frame(f)
        bar2.grid(row=2, column=0, sticky="e")
        self.btn_adjust = ttk.Button(bar2, text="Điều chỉnh tồn…", command=self.on_adjust)
        self.btn_history = ttk.Button(bar2, text="Sổ kho", command=self.on_history)
        self.btn_adjust.pack(side="left", padx=3)
        self.btn_history.pack(side="left")
        if self.staff.role != StaffRole.WAREHOUSE:
            self.btn_adjust.state(["disabled"])          # chỉ nhân viên kho điều chỉnh tồn
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_stock_level = self.inventory_controller.search_stock_level(
            self.cbo_stock_location.value(), self.txt_keyword.get(), self.var_below_reorder_point.get())
        fill_table(self.tbl_stock_level, [(l.id, (l.sku, l.style_name, f"{l.colour}/{l.size_label}", l.location_name,
                                                  l.on_hand, l.reserved, l.available, l.reorder_point),
                                           ("bad",) if l.available <= l.reorder_point else ())
                                          for l in self.list_stock_level])

    @guarded
    def on_adjust(self) -> None:
        level = selected(self.tbl_stock_level, self.list_stock_level)
        if level is None:
            return warn(self, "Chọn một dòng tồn kho")
        modal(AdjustStockFrm(self.staff, level), self)
        self.on_search()

    @guarded
    def on_history(self) -> None:
        level = selected(self.tbl_stock_level, self.list_stock_level)
        if level is None:
            return warn(self, "Chọn một dòng tồn kho")
        StockMovementFrm(ProductVariant(id=level.productVariantId, sku=level.sku, colour=level.colour,
                                           size_label=level.size_label))
