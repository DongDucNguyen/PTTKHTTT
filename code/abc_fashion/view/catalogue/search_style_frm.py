"""SearchStyleFrm — Tìm kiếm bằng chữ, ảnh, giọng nói (UC05)."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk

from abc_fashion.controller.catalogue_controller import CatalogueController
from abc_fashion.model.catalogue import Style
from abc_fashion.model.user import Customer
from abc_fashion.view import _theme
from abc_fashion.view._util import (body, entry_set, fill_table, guarded, make_table, message_label, money, read_file,
                                    record_wav, run_in_thread, selected, show, show_image, warn)
from abc_fashion.view.catalogue.style_detail_frm import StyleDetailFrm

RECORD_SECONDS = 5


class SearchStyleFrm(tk.Toplevel):
    def __init__(self, customer: Customer | None, keyword: str):
        super().__init__()
        self.customer = customer
        self.list_style: list[Style] = []
        self.catalogue_controller = CatalogueController()
        self._build()
        if keyword:
            entry_set(self.txt_keyword, keyword)
            self.on_search()

    def _build(self) -> None:
        f = body(self, "Tìm kiếm")
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, sticky="we")
        self.txt_keyword = ttk.Entry(bar, width=36)
        self.txt_keyword.pack(side="left")
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search, style="Primary.TButton",
                                     image=_theme.icon(self, "search", 18, "#FFFFFF"), compound="left")
        self.btn_search.pack(side="left", padx=3)
        self.btn_search_by_image = ttk.Button(bar, text="Bằng ảnh…", command=self.on_search_by_image,
                                              image=_theme.icon(self, "image", 18), compound="left")
        self.btn_search_by_image.pack(side="left", padx=3)
        self.btn_search_by_voice = ttk.Button(bar, text="Nói để tìm", command=self.on_search_by_voice,
                                              image=_theme.icon(self, "mic", 18), compound="left")
        self.btn_search_by_voice.pack(side="left", padx=3)
        self.btn_voice_file = ttk.Button(bar, text="File âm thanh…", command=self._voice_from_file)
        self.btn_voice_file.pack(side="left", padx=3)
        self.cnv_query_image = tk.Canvas(f, width=120, height=120, highlightthickness=0)
        self.cnv_query_image.grid(row=1, column=1, sticky="n", padx=(8, 0), pady=8)
        self.tbl_style = make_table(f, [("code", "Mã", 80), ("name", "Sản phẩm", 260), ("brand", "Thương hiệu", 120),
                                        ("price", "Giá từ", 100)], height=14)
        self.tbl_style.box.grid(row=1, column=0, sticky="nsew", pady=8)
        self.tbl_style.bind("<Double-1>", lambda e: self.on_open_style())
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=2, column=0, sticky="w")
        ttk.Button(f, text="Xem chi tiết", command=self.on_open_style).grid(row=2, column=0, sticky="e")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    def _search_async(self, work, what: str, empty_hint: str) -> None:
        """Gọi dịch vụ AI ở luồng phụ (CLIP / Whisper có thể mất vài giây) rồi quay về luồng giao diện: chỉ luồng
        giao diện được đọc CSDL và chạm widget."""
        self._lock_buttons(True)
        show(self.lbl_message, f"Đang tìm bằng {what}…", ok=True)

        run_in_thread(self, work, lambda result: self._search_done(result, what, empty_hint))

    @guarded
    def _search_done(self, result, what: str, empty_hint: str) -> None:
        self._lock_buttons(False)
        if isinstance(result, Exception):
            return show(self.lbl_message, f"Tìm bằng {what} tạm thời không dùng được ({result}). Hãy tìm bằng chữ.")
        self._show(self.catalogue_controller.get_active_styles(result), empty_hint)

    def _lock_buttons(self, busy: bool) -> None:
        for b in (self.btn_search, self.btn_search_by_image, self.btn_search_by_voice, self.btn_voice_file):
            b.state(["disabled"] if busy else ["!disabled"])

    def _show(self, styles: list[Style], empty_hint: str) -> None:
        self.list_style = styles
        fill_table(self.tbl_style, [(s.id, (s.code, s.name, s.brand or "", money(getattr(s, "min_price", 0))))
                                    for s in self.list_style])
        show(self.lbl_message, "" if self.list_style else empty_hint)

    @guarded
    def on_search(self) -> None:
        key = self.txt_keyword.get().strip()
        self.cnv_query_image.delete("all")
        self._show(self.catalogue_controller.search_style(key),
                   f"Không tìm thấy \"{key}\". Hãy thử từ khoá khác, ví dụ: áo, váy, jeans.")

    @guarded
    def on_search_by_image(self) -> None:
        path = filedialog.askopenfilename(parent=self, title="Chọn ảnh",
                                          filetypes=[("Ảnh", "*.jpg *.jpeg *.png"), ("Tất cả", "*.*")])
        if not path:
            return
        show_image(self.cnv_query_image, path, (120, 120))
        data = read_file(path)
        self._search_async(lambda: self.catalogue_controller.find_style_ids_by_image(data), "ảnh",
                           "Không tìm thấy sản phẩm giống ảnh. Hãy tìm bằng chữ.")

    @guarded
    def on_search_by_voice(self) -> None:
        """Ghi âm vài giây từ micro rồi tìm (UC05, mục 8.2); không có micro thì cho chọn file âm thanh."""
        self._lock_buttons(True)
        self.cnv_query_image.delete("all")
        self._countdown(RECORD_SECONDS)
        run_in_thread(self, lambda: record_wav(RECORD_SECONDS), self._recorded)

    def _countdown(self, left: int) -> None:
        """Đếm ngược trong lúc luồng phụ đang ghi âm (dừng khi nút đã mở lại)."""
        if left <= 0 or "disabled" not in self.btn_search_by_voice.state():
            return
        show(self.lbl_message, f"Đang nghe… hãy nói tên sản phẩm ({left} giây)", ok=True)
        self.after(1000, lambda: self._countdown(left - 1))

    @guarded
    def _recorded(self, result) -> None:
        self._lock_buttons(False)
        if isinstance(result, Exception):
            show(self.lbl_message, f"Không ghi âm được: {result}. Hãy chọn một file âm thanh.")
            return self._voice_from_file()
        self._search_async(lambda: self.catalogue_controller.find_style_ids_by_voice(result), "giọng nói",
                           "Không nhận ra sản phẩm trong câu nói. Hãy thử nói rõ hơn hoặc tìm bằng chữ.")

    @guarded
    def _voice_from_file(self) -> None:
        path = filedialog.askopenfilename(parent=self, title="Chọn file ghi âm (hoặc bản ghi .txt)",
                                          filetypes=[("Âm thanh / bản ghi", "*.wav *.mp3 *.m4a *.txt"), ("Tất cả", "*.*")])
        if not path:
            return
        data = read_file(path)
        self.cnv_query_image.delete("all")
        self._search_async(lambda: self.catalogue_controller.find_style_ids_by_voice(data), "giọng nói",
                           "Không nhận ra sản phẩm trong câu nói. Hãy tìm bằng chữ.")

    @guarded
    def on_open_style(self) -> None:
        s = selected(self.tbl_style, self.list_style)
        if s is None:
            return warn(self, "Chọn một sản phẩm")
        StyleDetailFrm(self.customer, s)
