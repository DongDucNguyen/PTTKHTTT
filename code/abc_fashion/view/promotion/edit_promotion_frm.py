"""EditPromotionFrm — Thêm / sửa khuyến mãi, style áp dụng, voucher (UC15, UC27)."""
from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from abc_fashion.controller.promotion_controller import PromotionController
from abc_fashion.model.catalogue import Style
from abc_fashion.model.sales import DiscountType, PromoType, PromotionStatus, Promotion, Voucher
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, DateEntry, body, entry_set, enum_choices, fill_table, guarded, label,
                                    make_table, message_label, modal, selected, show, to_int)
from abc_fashion.view.promotion.select_style_frm import SelectStyleFrm


class EditPromotionFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, promotion: Promotion | None):
        super().__init__()
        self.staff = staff
        self.promotion_controller = PromotionController()
        self.promotion = promotion or Promotion(status=PromotionStatus.DRAFT)
        self.list_style: list[Style] = []
        self.list_voucher: list[Voucher] = []
        self._build()
        self.on_reset()

    def _build(self) -> None:
        f = body(self, "Khuyến mãi")
        g = ttk.Frame(f)
        g.grid(row=0, column=0, sticky="nw")
        self.txt_name = ttk.Entry(g, width=36)
        self.cbo_promo_type = ChoiceBox(g, [(label(t), t) for t in PromoType])
        self.cbo_discount_type = ChoiceBox(g, [("Phần trăm (%)", DiscountType.PERCENT),
                                               ("Số tiền cố định (đ)", DiscountType.FIXED_AMOUNT)])
        self.txt_discount_value = ttk.Entry(g, width=14)
        self.txt_min_order_value = ttk.Entry(g, width=14)
        self.dte_starts_at, self.dte_ends_at = DateEntry(g), DateEntry(g)
        self.cbo_status = ChoiceBox(g, enum_choices(PromotionStatus))
        for r, (t, w) in enumerate([("Tên", self.txt_name), ("Loại", self.cbo_promo_type),
                                    ("Kiểu giảm", self.cbo_discount_type), ("Giá trị giảm", self.txt_discount_value),
                                    ("Đơn tối thiểu (đ)", self.txt_min_order_value), ("Bắt đầu", self.dte_starts_at),
                                    ("Kết thúc (hết ngày)", self.dte_ends_at), ("Trạng thái", self.cbo_status)]):
            ttk.Label(g, text=t).grid(row=r, column=0, sticky="w", pady=2, padx=(0, 6))
            w.grid(row=r, column=1, sticky="w", pady=2)
        ttk.Label(g, text="Không có mã giảm giá = tự động giảm giá trên trang sản phẩm.",
                  style="Muted.TLabel").grid(row=8, column=0, columnspan=2, sticky="w", pady=4)

        side = ttk.Frame(f)
        side.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(side, text="Style áp dụng").grid(row=0, column=0, sticky="w")
        self.tbl_style = make_table(side, [("code", "Mã", 80), ("name", "Tên", 200)], height=6)
        self.tbl_style.box.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.btn_add_style = ttk.Button(side, text="Chọn style…", command=self.on_add_style)
        self.btn_add_style.grid(row=2, column=0, sticky="w", pady=3)
        self.btn_remove_style = ttk.Button(side, text="Bỏ style", command=self.on_remove_style)
        self.btn_remove_style.grid(row=2, column=1, sticky="w")
        ttk.Label(side, text="Mã giảm giá").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.tbl_voucher = make_table(side, [("code", "Mã", 120), ("limit", "Giới hạn", 70), ("used", "Đã dùng", 70)],
                                      height=5)
        self.tbl_voucher.box.grid(row=4, column=0, columnspan=3, sticky="nsew")
        vb = ttk.Frame(side)
        vb.grid(row=5, column=0, columnspan=3, sticky="w", pady=3)
        self.txt_voucher_code = ttk.Entry(vb, width=14)
        self.txt_voucher_code.pack(side="left")
        self.spn_usage_limit = ttk.Spinbox(vb, from_=1, to=100000, width=7)
        self.spn_usage_limit.set(100)
        self.spn_usage_limit.pack(side="left", padx=4)
        self.btn_add_voucher = ttk.Button(vb, text="Thêm mã", command=self.on_add_voucher)
        self.btn_add_voucher.pack(side="left")

        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=1, column=0, columnspan=2, sticky="w")
        bar = ttk.Frame(f)
        bar.grid(row=2, column=0, columnspan=2, sticky="e", pady=6)
        self.btn_reset = ttk.Button(bar, text="Khôi phục", command=self.on_reset)
        self.btn_reset.pack(side="left", padx=3)
        self.btn_save = ttk.Button(bar, text="Lưu", command=self.on_save)
        self.btn_save.pack(side="left")

    def _refresh(self) -> None:
        fill_table(self.tbl_style, [(s.id, (s.code, s.name)) for s in self.list_style])
        fill_table(self.tbl_voucher, [(v.id, (v.code, v.usage_limit, v.used_count)) for v in self.list_voucher])
        self.btn_add_voucher.state(["!disabled"] if self.promotion.id else ["disabled"])

    @guarded
    def on_add_style(self) -> None:
        frm = SelectStyleFrm(self.list_style)
        modal(frm, self)
        self.list_style = frm.list_selected
        self._refresh()

    def on_remove_style(self) -> None:
        s = selected(self.tbl_style, self.list_style)
        if s is not None:
            self.list_style.remove(s)
            self._refresh()

    @guarded
    def on_add_voucher(self) -> None:
        self.list_voucher = self.promotion_controller.add_voucher(self.promotion, self.txt_voucher_code.get(),
                                                                  to_int(self.spn_usage_limit.get(), 0))
        self.txt_voucher_code.delete(0, "end")
        self._refresh()

    @guarded
    def on_save(self) -> None:
        self.promotion_controller.save_promotion(
            self.promotion, self.txt_name.get(), self.cbo_promo_type.value(), self.cbo_discount_type.value(),
            to_int(self.txt_discount_value.get()), to_int(self.txt_min_order_value.get() or "0"),
            self.dte_starts_at.get_date(), self.dte_ends_at.get_date(), self.cbo_status.value(), self.list_style)
        show(self.lbl_message, "Đã lưu", ok=True)
        self._refresh()

    def on_reset(self) -> None:
        p = self.promotion
        if p.id:
            self.promotion = p = self.promotion_controller.get_promotion_detail(p)
            self.list_style = list(p.styles)
            self.list_voucher = list(p.vouchers)
        entry_set(self.txt_name, p.name)
        self.cbo_promo_type.select_value(p.promo_type or PromoType.SEASONAL)
        self.cbo_discount_type.select_value(p.discount_type or DiscountType.PERCENT)
        entry_set(self.txt_discount_value, p.discount_value)
        entry_set(self.txt_min_order_value, p.min_order_value or 0)
        self.dte_starts_at.set_date(p.starts_at.date() if p.starts_at else date.today())
        self.dte_ends_at.set_date(p.ends_at.date() if p.ends_at else date.today() + timedelta(days=30))
        self.cbo_status.select_value(p.status)
        self.lbl_message.config(text="")
        self._refresh()
