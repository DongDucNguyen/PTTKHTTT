"""StockMovementFrm — Sổ kho của một biến thể."""
from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from abc_fashion.controller.inventory_controller import InventoryController
from abc_fashion.model.catalogue import ProductVariant
from abc_fashion.model.inventory import MovementReason, StockMovement
from abc_fashion.view._util import (ChoiceBox, DateEntry, body, enum_choices, fill_table, fmt_dt, guarded, label,
                                    make_table)


class StockMovementFrm(tk.Toplevel):
    def __init__(self, variant: ProductVariant):
        super().__init__()
        self.variant = variant
        self.list_movement: list[StockMovement] = []
        self.inventory_controller = InventoryController()
        f = body(self, f"Sổ kho — {variant.sku}")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        ttk.Label(bar, text="Từ").pack(side="left")
        self.dte_from = DateEntry(bar)
        self.dte_from.pack(side="left", padx=3)
        ttk.Label(bar, text="đến").pack(side="left")
        self.dte_to = DateEntry(bar)
        self.dte_to.pack(side="left", padx=3)
        self.cbo_reason = ChoiceBox(bar, enum_choices(MovementReason, "Mọi lý do"), width=12)
        self.cbo_reason.pack(side="left", padx=3)
        self.btn_view = ttk.Button(bar, text="Xem", command=self.on_view)
        self.btn_view.pack(side="left")
        self.tbl_movement = make_table(f, [("time", "Thời điểm", 130), ("change", "Thay đổi", 80),
                                           ("reason", "Lý do", 90), ("ref", "Tham chiếu", 130), ("loc", "Kho", 100),
                                           ("staff", "Nhân viên", 130), ("note", "Ghi chú", 180)], height=14)
        self.tbl_movement.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.lbl_total = ttk.Label(f)
        self.lbl_total.grid(row=2, column=0, sticky="w")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)
        self.dte_from.set_date(date.today() - timedelta(days=30))
        self.dte_to.set_date(date.today())
        self.on_view()

    @guarded
    def on_view(self) -> None:
        self.list_movement = self.inventory_controller.get_movements(self.variant, self.dte_from.get_date(),
                                                                     self.dte_to.get_date(), self.cbo_reason.value())
        fill_table(self.tbl_movement, [(m.id, (fmt_dt(m.created_at), f"{m.quantity_change:+d}", label(m.reason),
                                               m.reference or "", getattr(m, "location_name", ""),
                                               getattr(m, "staff_name", "") or "", m.note or ""))
                                       for m in self.list_movement])
        self.lbl_total.config(text=f"Tổng thay đổi trong kỳ: {sum(m.quantity_change for m in self.list_movement):+d}")
