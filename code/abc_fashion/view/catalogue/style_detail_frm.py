"""StyleDetailFrm — Trang chi tiết sản phẩm (UC06, UC33)."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.cart_controller import CartController
from abc_fashion.controller.catalogue_controller import CatalogueController
from abc_fashion.model.catalogue import MediaType, ProductMedia, ProductVariant, Style
from abc_fashion.model.inventory import availability_text
from abc_fashion.model.review import Review
from abc_fashion.model.user import Customer
from abc_fashion.view import _theme
from abc_fashion.view._util import (ERROR_FG, OK_FG, body, fill_table, fmt_dt, guarded, info, label, make_table, money, show,
                                    media_path, open_media, show_image, text_set, warn)
from abc_fashion.view.catalogue.assistant_frm import AssistantFrm

MEDIA_SIZE = (260, 300)


class StyleDetailFrm(tk.Toplevel):
    def __init__(self, customer: Customer | None, style: Style):
        super().__init__()
        self.customer = customer
        self.catalogue_controller = CatalogueController()
        self.cart_controller = CartController()
        # style kèm biến thể, ảnh, vật liệu, bảng cỡ, đánh giá, khuyến mãi (cũng là ngữ cảnh cho trợ lý AI)
        self.style = self.catalogue_controller.get_style_detail(style)
        self.list_variant: list[ProductVariant] = self.style.variants
        self.list_media: list[ProductMedia] = self.style.media
        self._images = self.style.images                                                   # canvas chỉ hiện ảnh
        self._videos = [m for m in self.list_media if m.media_type == MediaType.VIDEO]     # video mở bằng trình phát hệ thống
        self.list_review: list[Review] = self.style.reviews
        self.selected_variant: ProductVariant | None = None
        self.promotion = self.style.promotion
        self.materials = self.style.materials
        self.size_chart = self.style.size_chart
        self._media_index = 0
        self._build()
        self._fill()

    def _build(self) -> None:
        f = body(self, self.style.name)
        left = ttk.Frame(f)
        left.grid(row=0, column=0, sticky="n", padx=(0, 12))
        self.cnv_media = tk.Canvas(left, width=MEDIA_SIZE[0], height=MEDIA_SIZE[1], highlightthickness=0)
        self.cnv_media.pack()
        nav = ttk.Frame(left)
        nav.pack(pady=4)
        ttk.Button(nav, text="◀", width=3, command=lambda: self._show_media(-1)).pack(side="left")
        ttk.Button(nav, text="▶", width=3, command=lambda: self._show_media(+1)).pack(side="left")
        self.btn_play_video = ttk.Button(left, text="Xem video", command=self._play_video,
                                         image=_theme.icon(self, "play", 16), compound="left")
        if any(self._video_available(m) for m in self._videos):             # video trên CDN không tải được thì không hiện nút
            self.btn_play_video.pack(pady=(0, 4))

        right = ttk.Frame(f)
        right.grid(row=0, column=1, sticky="nw")
        self.lbl_name = ttk.Label(right, style="H2.TLabel", wraplength=380)
        self.lbl_name.grid(row=0, column=0, columnspan=3, sticky="w")
        self.lbl_brand = ttk.Label(right, style="Muted.TLabel")
        self.lbl_brand.grid(row=1, column=0, columnspan=3, sticky="w")
        self.lbl_price = ttk.Label(right, style="Price.TLabel")
        self.lbl_price.grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))
        self.lbl_promotion = ttk.Label(right, style="Promo.TLabel")
        self.lbl_promotion.grid(row=3, column=0, columnspan=3, sticky="w")
        ttk.Label(right, text="Màu").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.cbo_colour = ttk.Combobox(right, state="readonly", width=14)
        self.cbo_colour.grid(row=4, column=1, sticky="w", pady=(10, 0))
        self.cbo_colour.bind("<<ComboboxSelected>>", lambda e: self._on_colour())
        ttk.Label(right, text="Cỡ").grid(row=5, column=0, sticky="w")
        self.cbo_size = ttk.Combobox(right, state="readonly", width=14)
        self.cbo_size.grid(row=5, column=1, sticky="w")
        self.cbo_size.bind("<<ComboboxSelected>>", lambda e: self.on_select_variant())
        self.lbl_availability = ttk.Label(right)
        self.lbl_availability.grid(row=6, column=0, columnspan=3, sticky="w", pady=4)
        ttk.Label(right, text="Số lượng").grid(row=7, column=0, sticky="w")
        self.spn_quantity = ttk.Spinbox(right, from_=1, to=10, width=6)
        self.spn_quantity.set(1)
        self.spn_quantity.grid(row=7, column=1, sticky="w")
        self.btn_add_to_cart = ttk.Button(right, text="Thêm vào giỏ", command=self.on_add_to_cart)
        self.btn_add_to_cart.grid(row=8, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.btn_ask_assistant = ttk.Button(right, text="Hỏi trợ lý AI", command=self.on_ask_assistant)
        self.btn_ask_assistant.grid(row=8, column=2, sticky="w", pady=(10, 0))
        self.lbl_message = ttk.Label(right, wraplength=380)
        self.lbl_message.grid(row=9, column=0, columnspan=3, sticky="w", pady=4)

        nb = ttk.Notebook(f)
        nb.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        desc = ttk.Frame(nb, padding=8)
        nb.add(desc, text="Mô tả")
        self.txa_description = tk.Text(desc, height=4, width=70, wrap="word")
        self.txa_description.pack(fill="x")
        self.lbl_material = ttk.Label(desc, wraplength=600)
        self.lbl_material.pack(anchor="w", pady=2)
        self.lbl_care_instructions = ttk.Label(desc, wraplength=600)
        self.lbl_care_instructions.pack(anchor="w", pady=2)
        self.lbl_model_info = ttk.Label(desc, wraplength=600)
        self.lbl_model_info.pack(anchor="w", pady=2)
        size_tab = ttk.Frame(nb, padding=8)
        nb.add(size_tab, text="Bảng cỡ")
        measures = sorted({e.measure for e in self.size_chart}, key=lambda m: list(type(m)).index(m))
        self._measures = measures
        self.tbl_size_chart = make_table(size_tab, [("size", "Cỡ", 70)] + [(m.value, m.value, 90) for m in measures],
                                         height=5)
        self.tbl_size_chart.box.pack(fill="both", expand=True)
        rev = ttk.Frame(nb, padding=8)
        nb.add(rev, text=f"Đánh giá ({len(self.list_review)})")
        self.lbl_review_summary = ttk.Label(rev, wraplength=640, justify="left")
        self.lbl_review_summary.pack(anchor="w", pady=(0, 6))
        self.tbl_review = make_table(rev, [("rating", "Sao", 50), ("variant", "Màu / cỡ", 100), ("fit", "Độ vừa", 90),
                                           ("body", "Nội dung", 380), ("date", "Ngày", 90)], height=6)
        self.tbl_review.box.pack(fill="both", expand=True)
        f.rowconfigure(1, weight=1)
        f.columnconfigure(1, weight=1)

    def _fill(self) -> None:
        s = self.style
        self.lbl_name.config(text=s.name)
        self.lbl_brand.config(text=f"{s.brand or ''} · {getattr(s, 'category_name', '')} · mã {s.code}")
        text_set(self.txa_description, s.description or "", readonly=True)
        self.lbl_material.config(text="Chất liệu: " + (", ".join(f"{m.material} {m.percent}%" for m in self.materials)
                                                      or "—"))
        self.lbl_care_instructions.config(text="Bảo quản: " + (s.care_instructions or "—"))
        self.lbl_model_info.config(text=f"Dáng: {s.fit_type.value if s.fit_type else '—'}. {s.model_info or ''}")
        by_size: dict[str, dict] = {}
        for e in self.size_chart:
            by_size.setdefault(e.size_label, {})[e.measure] = e.value_cm
        fill_table(self.tbl_size_chart, [(size, [size] + [f"{vals[m]:g}" if m in vals else "" for m in self._measures])
                                         for size, vals in by_size.items()])
        fill_table(self.tbl_review, [(r.id, ("★" * r.rating, f"{getattr(r, 'colour', '')}/{getattr(r, 'size_label', '')}",
                                             label(r.fit_vote), r.body, fmt_dt(r.created_at)[:10]))
                                     for r in self.list_review])
        summary = self.catalogue_controller.summarise_reviews(self.style)                    # UC33
        self.lbl_review_summary.config(text=("Tóm tắt: " + summary) if summary else "Chưa có đánh giá.")
        if self.promotion is not None:
            how = "giá đã giảm" if not getattr(self.promotion, "voucher_count", 0) else "nhập mã khi thanh toán"
            self.lbl_promotion.config(text=f"Khuyến mãi: {self.promotion.name} ({how})")
        colours = list(dict.fromkeys(v.colour for v in self.list_variant))
        self.cbo_colour["values"] = colours
        if colours:
            self.cbo_colour.current(0)
            self._on_colour()
        else:
            self.lbl_price.config(text="Tạm ngừng bán")
            self.btn_add_to_cart.state(["disabled"])
        self._show_media(0)

    @staticmethod
    def _video_available(m: ProductMedia) -> bool:
        path = media_path(m.url)                            # None với URL CDN (không phát được ở máy này)
        return bool(path) and os.path.exists(path)

    @guarded
    def _play_video(self) -> None:
        video = next((m for m in self._videos if self._video_available(m)), None)
        if video is None or not open_media(video.url):
            warn(self, "Không mở được video")

    def _show_media(self, step: int) -> None:
        if not self._images:
            return show_image(self.cnv_media, None, MEDIA_SIZE)
        self._media_index = (self._media_index + step) % len(self._images)
        show_image(self.cnv_media, self._images[self._media_index].url, MEDIA_SIZE)

    def _on_colour(self) -> None:
        colour = self.cbo_colour.get()
        sizes = [v.size_label for v in self.list_variant if v.colour == colour]
        self.cbo_size["values"] = sizes
        if sizes:
            self.cbo_size.current(0)
        for i, m in enumerate(self._images):               # ảnh theo màu nếu có
            if m.colour == colour:
                self._media_index = i
                show_image(self.cnv_media, m.url, MEDIA_SIZE)
                break
        self.on_select_variant()

    @guarded
    def on_select_variant(self) -> None:
        colour, size = self.cbo_colour.get(), self.cbo_size.get()
        self.selected_variant = next((v for v in self.list_variant if v.colour == colour and v.size_label == size), None)
        v = self.selected_variant
        if v is None:
            return
        final = self.catalogue_controller.get_final_price(self.style, v)
        self.lbl_price.config(text=money(v.price) if final == v.price else f"{money(final)}   (giá gốc {money(v.price)})")
        level = self.catalogue_controller.get_stock_level(v)
        available = level.available if level else 0
        self.lbl_availability.config(text=availability_text(level), foreground=ERROR_FG if available <= 0 else OK_FG)
        self.spn_quantity.config(to=max(available, 1))
        self.btn_add_to_cart.state(["!disabled"] if available > 0 else ["disabled"])

    @guarded
    def on_add_to_cart(self) -> None:
        if self.customer is None:
            return warn(self, "Vui lòng đăng nhập để mua hàng")
        try:
            qty = int(self.spn_quantity.get())
        except ValueError:
            return show(self.lbl_message, "Số lượng không hợp lệ")
        v = self.selected_variant
        self.cart_controller.add_to_cart(self.customer, v, qty)
        show(self.lbl_message, f"Đã thêm {qty} × {v.sku} vào giỏ", ok=True)
        info(self, "Đã thêm vào giỏ hàng")

    @guarded
    def on_ask_assistant(self) -> None:
        AssistantFrm(self.customer, self.style)
