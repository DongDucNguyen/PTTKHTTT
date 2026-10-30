"""EditVariantFrm — Thêm / sửa một biến thể (SKU)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.product_controller import ProductController
from abc_fashion.model.catalogue import VariantStatus, ProductVariant, Style
from abc_fashion.model.inventory import StockLocation
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, body, button_row, entry_set, enum_choices, form_rows, guarded,
                                    message_label, to_int)


class EditVariantFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, style: Style, variant: ProductVariant | None):
        super().__init__()
        self.staff = staff
        self.style = style
        self.variant = variant
        self.product_controller = ProductController()
        self.list_stock_location: list[StockLocation] = self.product_controller.get_stock_locations()
        self.saved = False
        self._build()
        self.on_reset()

    def _build(self) -> None:
        f = body(self, f"Biến thể — {self.style.code}")
        self.txt_sku = ttk.Entry(f, width=24)
        self.txt_size_label = ttk.Entry(f, width=24)
        self.txt_colour = ttk.Entry(f, width=24)
        self.txt_price = ttk.Entry(f, width=24)
        self.cbo_status = ChoiceBox(f, enum_choices(VariantStatus))
        self.cbo_stock_location = ChoiceBox(f, [(l.name, l) for l in self.list_stock_location])
        self.spn_reorder_point = ttk.Spinbox(f, from_=0, to=9999, width=8)
        r = form_rows(f, [("SKU", self.txt_sku), ("Cỡ", self.txt_size_label), ("Màu", self.txt_colour),
                          ("Giá (đ)", self.txt_price), ("Trạng thái", self.cbo_status),
                          ("Kho (chỉ khi thêm mới)", self.cbo_stock_location), ("Điểm đặt hàng lại", self.spn_reorder_point)])
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=r, column=0, columnspan=2, sticky="w")
        self.btn_reset = ttk.Button(f, text="Khôi phục", command=self.on_reset)
        self.btn_save = ttk.Button(f, text="Lưu", command=self.on_save)
        button_row(f, [self.btn_reset, self.btn_save], r + 1)

    @guarded
    def on_save(self) -> None:
        v = ProductVariant(id=self.variant.id if self.variant else None, styleId=self.style.id,
                           sku=self.txt_sku.get(), size_label=self.txt_size_label.get(), colour=self.txt_colour.get(),
                           price=to_int(self.txt_price.get()), status=self.cbo_status.value())
        self.product_controller.save_variant(self.style, v, self.cbo_stock_location.value(),
                                             to_int(self.spn_reorder_point.get(), 0))
        self.variant, self.saved = v, True
        self.destroy()

    def on_reset(self) -> None:
        v = self.variant
        entry_set(self.txt_sku, v.sku if v else f"{self.style.code.replace('ST-', '')}-")
        entry_set(self.txt_size_label, v.size_label if v else "")
        entry_set(self.txt_colour, v.colour if v else "")
        entry_set(self.txt_price, v.price if v else "")
        self.cbo_status.select_value(v.status if v else VariantStatus.ACTIVE)
        self.spn_reorder_point.set(5)
        if v and v.id:
            self.cbo_stock_location.select_value(getattr(v, "stockLocationId", None),
                                                 key=lambda x: x.id if isinstance(x, StockLocation) else x)
            self.cbo_stock_location.state(["disabled"])
            self.spn_reorder_point.state(["disabled"])
        self.lbl_message.config(text="")
