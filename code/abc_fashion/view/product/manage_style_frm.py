"""ManageStyleFrm — Danh sách sản phẩm cho quản trị (UC21)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.product_controller import ProductController
from abc_fashion.model.catalogue import StyleStatus, Style
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, body, confirm, enum_choices, fill_table, guarded, label, make_table, modal,
                                    money, selected, warn)
from abc_fashion.view.product.edit_style_frm import EditStyleFrm


class ManageStyleFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_style: list[Style] = []
        self.product_controller = ProductController()
        self._categories = self.product_controller.get_categories()
        self._build()
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Quản lý sản phẩm")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.txt_keyword = ttk.Entry(bar, width=26)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.cbo_category = ChoiceBox(bar, [("Mọi danh mục", None)] + [(c.name, c) for c in self._categories], width=16)
        self.cbo_category.pack(side="left", padx=4)
        self.cbo_status = ChoiceBox(bar, enum_choices(StyleStatus, "Mọi trạng thái"), width=14)
        self.cbo_status.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_style = make_table(f, [("code", "Mã", 90), ("name", "Tên", 240), ("brand", "Thương hiệu", 110),
                                        ("cat", "Danh mục", 100), ("price", "Giá từ", 90), ("status", "Trạng thái", 90)],
                                    height=16)
        self.tbl_style.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_style.bind("<Double-1>", lambda e: self.on_edit())
        bar2 = ttk.Frame(f)
        bar2.grid(row=2, column=0, sticky="e")
        self.btn_add = ttk.Button(bar2, text="Thêm", command=self.on_add)
        self.btn_edit = ttk.Button(bar2, text="Sửa", command=self.on_edit)
        self.btn_deactivate = ttk.Button(bar2, text="Ngừng bán", command=self.on_deactivate)
        for b in (self.btn_add, self.btn_edit, self.btn_deactivate):
            b.pack(side="left", padx=3)
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_style = self.product_controller.search_style(self.txt_keyword.get(), self.cbo_category.value(),
                                                               self.cbo_status.value())
        fill_table(self.tbl_style, [(s.id, (s.code, s.name, s.brand or "", getattr(s, "category_name", ""),
                                            money(getattr(s, "min_price", None)) if getattr(s, "min_price", None) else "",
                                            label(s.status)), ("bad",) if s.status == StyleStatus.INACTIVE else ())
                                    for s in self.list_style])

    @guarded
    def on_add(self) -> None:
        modal(EditStyleFrm(self.staff, None), self)
        self.on_search()

    @guarded
    def on_edit(self) -> None:
        s = selected(self.tbl_style, self.list_style)
        if s is None:
            return warn(self, "Chọn một sản phẩm")
        modal(EditStyleFrm(self.staff, s), self)
        self.on_search()

    @guarded
    def on_deactivate(self) -> None:
        s = selected(self.tbl_style, self.list_style)
        if s is None:
            return warn(self, "Chọn một sản phẩm")
        if s.status == StyleStatus.INACTIVE or not confirm(self, f"Ngừng bán {s.code} – {s.name} và mọi biến thể?"):
            return
        self.product_controller.deactivate_style(self.staff, s)
        self.on_search()
