"""ManagePromotionFrm — Danh sách khuyến mãi (UC15)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.promotion_controller import PromotionController
from abc_fashion.model.sales import DiscountType, PromotionStatus, Promotion
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, body, confirm, enum_choices, fill_table, fmt_dt, guarded, label, make_table,
                                    modal, money, selected, warn)
from abc_fashion.view.promotion.edit_promotion_frm import EditPromotionFrm


def discount_text(p: Promotion) -> str:
    return f"{p.discount_value}%" if p.discount_type == DiscountType.PERCENT else money(p.discount_value)


class ManagePromotionFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_promotion: list[Promotion] = []
        self.promotion_controller = PromotionController()
        self._build()
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Quản lý khuyến mãi")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.txt_keyword = ttk.Entry(bar, width=26)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.cbo_status = ChoiceBox(bar, enum_choices(PromotionStatus, "Mọi trạng thái"), width=14)
        self.cbo_status.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_promotion = make_table(f, [("name", "Chương trình", 200), ("type", "Loại", 90), ("disc", "Giảm", 80),
                                            ("from", "Bắt đầu", 120), ("to", "Kết thúc", 120), ("styles", "Số style", 60),
                                            ("vouchers", "Số mã", 60), ("status", "Trạng thái", 90)], height=14)
        self.tbl_promotion.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_promotion.bind("<Double-1>", lambda e: self.on_edit())
        bar2 = ttk.Frame(f)
        bar2.grid(row=2, column=0, sticky="e")
        self.btn_add = ttk.Button(bar2, text="Thêm", command=self.on_add)
        self.btn_edit = ttk.Button(bar2, text="Sửa", command=self.on_edit)
        self.btn_end = ttk.Button(bar2, text="Kết thúc sớm", command=self.on_end)
        for b in (self.btn_add, self.btn_edit, self.btn_end):
            b.pack(side="left", padx=3)
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        self.list_promotion = self.promotion_controller.search_promotion(self.txt_keyword.get(), self.cbo_status.value())
        fill_table(self.tbl_promotion, [(p.id, (p.name, label(p.promo_type), discount_text(p), fmt_dt(p.starts_at),
                                                fmt_dt(p.ends_at), getattr(p, "style_count", ""),
                                                getattr(p, "voucher_count", ""), label(p.status)))
                                        for p in self.list_promotion])

    @guarded
    def on_add(self) -> None:
        modal(EditPromotionFrm(self.staff, None), self)
        self.on_search()

    @guarded
    def on_edit(self) -> None:
        p = selected(self.tbl_promotion, self.list_promotion)
        if p is None:
            return warn(self, "Chọn một chương trình")
        modal(EditPromotionFrm(self.staff, p), self)
        self.on_search()

    @guarded
    def on_end(self) -> None:
        p = selected(self.tbl_promotion, self.list_promotion)
        if p is None:
            return warn(self, "Chọn một chương trình")
        if p.status == PromotionStatus.ENDED or not confirm(self, f"Kết thúc chương trình \"{p.name}\" ngay?"):
            return
        self.promotion_controller.end_promotion(p)
        self.on_search()
