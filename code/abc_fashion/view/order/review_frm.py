"""ReviewFrm — Đánh giá sản phẩm đã mua (UC13, UC34)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.review_controller import ReviewController
from abc_fashion.model.review import FitVote, ReviewStatus
from abc_fashion.model.sales import OrderItem
from abc_fashion.model.user import Customer
from abc_fashion.view._util import body, entry_set, guarded, info, label, message_label, text_get


class ReviewFrm(tk.Toplevel):
    def __init__(self, customer: Customer, order_item: OrderItem):
        super().__init__()
        self.customer = customer
        self.order_item = order_item
        self.review_controller = ReviewController()
        self._build()

    def _build(self) -> None:
        it = self.order_item
        f = body(self, "Đánh giá sản phẩm")
        self.lbl_style_name = ttk.Label(f, text=getattr(it, "style_name", ""), style="H2.TLabel")
        self.lbl_style_name.grid(row=0, column=0, columnspan=4, sticky="w")
        self.lbl_variant = ttk.Label(f, text=f"{it.sku} · {it.colour} / {it.size_label}")
        self.lbl_variant.grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 6))
        ttk.Label(f, text="Số sao (1–5)").grid(row=2, column=0, sticky="w")
        self.spn_rating = ttk.Spinbox(f, from_=1, to=5, width=4)
        self.spn_rating.set(5)
        self.spn_rating.grid(row=2, column=1, sticky="w")
        ttk.Label(f, text="Cỡ đã mua").grid(row=2, column=2, sticky="e")
        self.txt_size_purchased = ttk.Entry(f, width=8)
        self.txt_size_purchased.grid(row=2, column=3, sticky="w")
        entry_set(self.txt_size_purchased, it.size_label)
        ttk.Label(f, text="Độ vừa").grid(row=3, column=0, sticky="w")
        self.var_fit_vote = tk.StringVar(value=FitVote.TRUE_TO_SIZE.value)
        self.rdo_fit_vote = []
        box = ttk.Frame(f)
        box.grid(row=3, column=1, columnspan=3, sticky="w")
        for v in FitVote:
            rb = ttk.Radiobutton(box, text=label(v), value=v.value, variable=self.var_fit_vote)
            rb.pack(side="left", padx=4)
            self.rdo_fit_vote.append(rb)
        ttk.Label(f, text="Nhận xét").grid(row=4, column=0, sticky="nw", pady=4)
        self.txa_body = tk.Text(f, height=6, width=56, wrap="word")
        self.txa_body.grid(row=4, column=1, columnspan=3, sticky="we", pady=4)
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=5, column=0, columnspan=3, sticky="w")
        self.btn_submit = ttk.Button(f, text="Gửi đánh giá", command=self.on_submit)
        self.btn_submit.grid(row=5, column=3, sticky="e")

    @guarded
    def on_submit(self) -> None:
        try:
            rating = int(self.spn_rating.get())
        except ValueError:
            rating = 0
        review = self.review_controller.submit_review(self.order_item, rating, text_get(self.txa_body),
                                                      self.txt_size_purchased.get(), FitVote(self.var_fit_vote.get()))
        info(self, "Cảm ơn bạn! Đánh giá đã được đăng." if review.status == ReviewStatus.APPROVED else
             f"Đánh giá đang chờ duyệt ({review.moderation_note}).")
        self.destroy()
