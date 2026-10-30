"""AdjustStockFrm — Điều chỉnh tồn có lý do (UC17, FR23)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.inventory import StockLevel
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import body, button_row, guarded, info, message_label, text_get


class AdjustStockFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, stock_level: StockLevel):
        super().__init__()
        self.staff = staff
        self.stock_level = stock_level
        self.inventory_controller = InventoryController()
        l = stock_level
        f = body(self, "Điều chỉnh tồn kho")
        self.lbl_sku = ttk.Label(f, text=f"{l.sku} – {getattr(l, 'style_name', '')}", style="H3.TLabel")
        self.lbl_stock_location = ttk.Label(f, text=f"Kho: {getattr(l, 'location_name', '')}")
        self.lbl_on_hand = ttk.Label(f, text=f"Tồn thực: {l.on_hand}")
        self.lbl_reserved = ttk.Label(f, text=f"Đang giữ cho đơn: {l.reserved}")
        for r, w in enumerate((self.lbl_sku, self.lbl_stock_location, self.lbl_on_hand, self.lbl_reserved)):
            w.grid(row=r, column=0, columnspan=2, sticky="w")
        ttk.Label(f, text="Số thay đổi (+ / −)").grid(row=4, column=0, sticky="w", pady=(8, 2))
        self.spn_quantity_change = ttk.Spinbox(f, from_=-100000, to=100000, width=8)
        self.spn_quantity_change.set(0)
        self.spn_quantity_change.grid(row=4, column=1, sticky="w", pady=(8, 2))
        ttk.Label(f, text="Tham chiếu (số biên bản…)").grid(row=5, column=0, sticky="w")
        self.txt_reference = ttk.Entry(f, width=30)
        self.txt_reference.grid(row=5, column=1, sticky="w")
        ttk.Label(f, text="Lý do / ghi chú").grid(row=6, column=0, sticky="nw", pady=4)
        self.txa_note = tk.Text(f, height=3, width=40, wrap="word")
        self.txa_note.grid(row=6, column=1, sticky="we", pady=4)
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=7, column=0, columnspan=2, sticky="w")
        self.btn_cancel = ttk.Button(f, text="Huỷ", command=self.on_cancel)
        self.btn_save = ttk.Button(f, text="Lưu", command=self.on_save)
        button_row(f, [self.btn_cancel, self.btn_save], 8)

    @guarded
    def on_save(self) -> None:
        try:
            change = int(self.spn_quantity_change.get())
        except ValueError:
            change = 0
        l = self.stock_level
        before = self.inventory_controller.adjust_stock(self.staff, l, change, self.txt_reference.get(),
                                                        text_get(self.txa_note))
        info(self, f"Đã điều chỉnh {l.sku}: tồn thực {before} → {l.on_hand}")
        self.destroy()

    def on_cancel(self) -> None:
        self.destroy()
