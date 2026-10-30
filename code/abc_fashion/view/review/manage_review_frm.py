"""ManageReviewFrm — Duyệt đánh giá (UC19)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.review_controller import ReviewController
from abc_fashion.model.review import ReviewStatus, Review
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, body, entry_set, enum_choices, fill_table, fmt_dt, guarded, label,
                                    make_table, message_label, selected, show, text_set, to_int)


class ManageReviewFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        self.list_review: list[Review] = []
        self.review_controller = ReviewController()
        self._build()
        self.cbo_status.select_value(ReviewStatus.PENDING)
        self.on_search()

    def _build(self) -> None:
        f = body(self, "Duyệt đánh giá")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="w")
        self.cbo_status = ChoiceBox(bar, enum_choices(ReviewStatus, "Mọi trạng thái"), width=14)
        self.cbo_status.pack(side="left")
        self.txt_keyword = ttk.Entry(bar, width=24)
        self.txt_keyword.pack(side="left", padx=4)
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        ttk.Label(bar, text="Sao (0 = tất cả)").pack(side="left")
        self.spn_rating = ttk.Spinbox(bar, from_=0, to=5, width=4)
        self.spn_rating.set(0)
        self.spn_rating.pack(side="left", padx=4)
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search)
        self.btn_search.pack(side="left")
        self.tbl_review = make_table(f, [("date", "Ngày", 110), ("style", "Sản phẩm", 170), ("cust", "Khách", 130),
                                         ("rating", "Sao", 50), ("body", "Nội dung", 280), ("status", "Trạng thái", 90)],
                                     height=10)
        self.tbl_review.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_review.bind("<<TreeviewSelect>>", lambda e: self.on_select_review())
        self.txa_body = tk.Text(f, height=5, width=80, wrap="word", state="disabled")
        self.txa_body.grid(row=2, column=0, sticky="we")
        mod = ttk.Frame(f)
        mod.grid(row=3, column=0, sticky="we", pady=6)
        ttk.Label(mod, text="Ghi chú kiểm duyệt").pack(side="left")
        self.txt_moderation_note = ttk.Entry(mod, width=50)
        self.txt_moderation_note.pack(side="left", padx=4)
        self.btn_approve = ttk.Button(mod, text="Duyệt", command=self.on_approve)
        self.btn_approve.pack(side="left", padx=3)
        self.btn_reject = ttk.Button(mod, text="Từ chối", command=self.on_reject)
        self.btn_reject.pack(side="left")
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=4, column=0, sticky="w")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    @guarded
    def on_search(self) -> None:
        rating = to_int(self.spn_rating.get(), 0) or None
        self.list_review = self.review_controller.search_review(self.txt_keyword.get(), self.cbo_status.value(), rating)
        fill_table(self.tbl_review, [(r.id, (fmt_dt(r.created_at), getattr(r, "style_name", ""),
                                             getattr(r, "customer_name", ""), "★" * r.rating,
                                             " ".join(r.body.split())[:80], label(r.status)))
                                     for r in self.list_review])
        text_set(self.txa_body, "", readonly=True)

    def on_select_review(self) -> None:
        r = selected(self.tbl_review, self.list_review)
        if r is None:
            return
        text_set(self.txa_body, f"{r.body}\n\nCỡ đã mua: {r.size_purchased or '—'} · Độ vừa: {label(r.fit_vote)}",
                 readonly=True)
        entry_set(self.txt_moderation_note, r.moderation_note)

    def _decide(self, status: ReviewStatus) -> None:
        r = selected(self.tbl_review, self.list_review)
        if r is None:
            return show(self.lbl_message, "Chọn một đánh giá")
        self.review_controller.moderate_review(self.staff, r, status, self.txt_moderation_note.get())
        show(self.lbl_message, f"Đã {label(status).lower()}", ok=True)
        self.on_search()

    @guarded
    def on_approve(self) -> None:
        self._decide(ReviewStatus.APPROVED)

    @guarded
    def on_reject(self) -> None:
        self._decide(ReviewStatus.REJECTED)
