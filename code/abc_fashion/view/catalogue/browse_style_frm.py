"""BrowseStyleFrm — Duyệt sản phẩm theo danh mục có bộ lọc (UC04). `customer` có thể `None`."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.catalogue_controller import COLOURS, SIZES, SORTS, CatalogueController
from abc_fashion.model.catalogue import FitType, Category, Style
from abc_fashion.model.user import Customer
from abc_fashion.view._util import ChoiceBox, body, enum_choices, fill_table, guarded, make_table, money, selected, to_int, warn
from abc_fashion.view.catalogue.style_detail_frm import StyleDetailFrm


class BrowseStyleFrm(tk.Toplevel):
    def __init__(self, customer: Customer | None):
        super().__init__()
        self.customer = customer
        self.catalogue_controller = CatalogueController()
        self.list_category: list[Category] = self.catalogue_controller.get_categories()
        self.list_style: list[Style] = []
        self._category: Category | None = None
        self._build()
        self._fill_tree()
        self.on_filter()

    def _build(self) -> None:
        f = body(self, "Duyệt sản phẩm")
        self.tree_category = ttk.Treeview(f, show="tree", height=18, selectmode="browse")
        self.tree_category.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 8))
        self.tree_category.bind("<<TreeviewSelect>>", lambda e: self.on_select_category())
        bar = ttk.Frame(f)
        bar.grid(row=0, column=1, sticky="w")
        ttk.Label(bar, text="Cỡ").grid(row=0, column=0)
        self.cbo_size = ttk.Combobox(bar, values=[""] + SIZES, width=6)
        self.cbo_size.grid(row=0, column=1, padx=3)
        ttk.Label(bar, text="Màu").grid(row=0, column=2)
        self.cbo_colour = ttk.Combobox(bar, values=[""] + COLOURS, width=8)
        self.cbo_colour.grid(row=0, column=3, padx=3)
        ttk.Label(bar, text="Dáng").grid(row=0, column=4)
        self.cbo_fit_type = ChoiceBox(bar, enum_choices(FitType, "Tất cả"), width=10)
        self.cbo_fit_type.grid(row=0, column=5, padx=3)
        ttk.Label(bar, text="Giá từ").grid(row=1, column=0)
        self.txt_min_price = ttk.Entry(bar, width=10)
        self.txt_min_price.grid(row=1, column=1, padx=3, pady=3)
        ttk.Label(bar, text="đến").grid(row=1, column=2)
        self.txt_max_price = ttk.Entry(bar, width=10)
        self.txt_max_price.grid(row=1, column=3, padx=3)
        ttk.Label(bar, text="Sắp xếp").grid(row=1, column=4)
        self.cbo_sort = ChoiceBox(bar, SORTS, width=12)
        self.cbo_sort.grid(row=1, column=5, padx=3)
        self.btn_filter = ttk.Button(bar, text="Lọc", command=self.on_filter)
        self.btn_filter.grid(row=0, column=6, rowspan=2, padx=6)
        self.tbl_style = make_table(f, [("name", "Sản phẩm", 260), ("brand", "Thương hiệu", 120),
                                        ("price", "Giá từ", 100)], height=16)
        self.tbl_style.box.grid(row=1, column=1, sticky="nsew", pady=(8, 0))
        self.tbl_style.bind("<Double-1>", lambda e: self.on_open_style())
        ttk.Button(f, text="Xem chi tiết", command=self.on_open_style).grid(row=2, column=1, sticky="e", pady=6)
        f.rowconfigure(1, weight=1)
        f.columnconfigure(1, weight=1)

    def _fill_tree(self) -> None:
        self.tree_category.insert("", "end", iid="all", text="Tất cả", open=True)
        pending = list(self.list_category)
        while pending:                                         # cha trước con
            rest = []
            for c in pending:
                parent = "all" if c.parentId is None else str(c.parentId)
                if parent == "all" or self.tree_category.exists(parent):
                    self.tree_category.insert(parent, "end", iid=str(c.id), text=c.name, open=True)
                else:
                    rest.append(c)
            if len(rest) == len(pending):
                break
            pending = rest

    @guarded
    def on_select_category(self) -> None:
        sel = self.tree_category.selection()
        self._category = next((c for c in self.list_category if sel and str(c.id) == sel[0]), None)
        self.on_filter()

    @guarded
    def on_filter(self) -> None:
        lo, hi = self.txt_min_price.get().strip(), self.txt_max_price.get().strip()
        if (lo and to_int(lo) is None) or (hi and to_int(hi) is None):
            return warn(self, "Giá phải là số")
        self.list_style = self.catalogue_controller.browse_style(
            self._category, self.cbo_size.get(), self.cbo_colour.get(), self.cbo_fit_type.value(),
            to_int(lo, 0) if lo else 0, to_int(hi, 0) if hi else 0, self.cbo_sort.value())
        fill_table(self.tbl_style, [(s.id, (s.name, s.brand or "", money(getattr(s, "min_price", 0))))
                                    for s in self.list_style])

    @guarded
    def on_open_style(self) -> None:
        s = selected(self.tbl_style, self.list_style)
        if s is None:
            return warn(self, "Chọn một sản phẩm")
        StyleDetailFrm(self.customer, s)
