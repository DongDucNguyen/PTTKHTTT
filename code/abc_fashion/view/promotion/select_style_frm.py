"""SelectStyleFrm — Chọn nhiều style (dùng ở EditPromotionFrm). Kết quả ở `list_selected`."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.promotion_controller import PromotionController
from abc_fashion.model.catalogue import Style
from abc_fashion.view._util import ChoiceBox, body, fill_table, guarded, label, make_table, selected_all


class SelectStyleFrm(tk.Toplevel):
    def __init__(self, selected: list[Style]):
        super().__init__()
        self.promotion_controller = PromotionController()
        self.list_style: list[Style] = []
        self.list_selected: list[Style] = list(selected)
        self._categories = self.promotion_controller.get_categories()
        self._build()
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Chọn style")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.txt_keyword = ttk.Entry(bar, width=24)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.cbo_category = ChoiceBox(bar, [("Mọi danh mục", None)] + [(c.name, c) for c in self._categories], width=16)
        self.cbo_category.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_style = make_table(f, [("code", "Mã", 90), ("name", "Tên", 240), ("status", "Trạng thái", 90),
                                        ("chosen", "Đã chọn", 60)], height=14, selectmode="extended")
        self.tbl_style.box.grid(row=1, column=0, sticky="nsew", pady=8)
        ttk.Label(f, text="Giữ Ctrl / Shift để chọn nhiều dòng.", style="Muted.TLabel").grid(row=2, column=0, sticky="w")
        self.btn_select = ttk.Button(f, text="Chọn", command=self.on_select)
        self.btn_select.grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_style = styles = self.promotion_controller.search_style(self.txt_keyword.get(),
                                                                          self.cbo_category.value())
        chosen = {s.id for s in self.list_selected}
        fill_table(self.tbl_style, [(s.id, (s.code, s.name, label(s.status), "✓" if s.id in chosen else ""),
                                     ("mark",) if s.id in chosen else ()) for s in styles])

    def on_select(self) -> None:
        have = {s.id for s in self.list_selected}
        self.list_selected += [s for s in selected_all(self.tbl_style, self.list_style) if s.id not in have]
        self.destroy()
