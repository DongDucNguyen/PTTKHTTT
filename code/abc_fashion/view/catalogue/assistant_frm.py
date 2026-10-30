"""AssistantFrm — Hỏi trợ lý AI về sản phẩm (UC32)."""
from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.catalogue_controller import CatalogueController
from abc_fashion.model.assistant import AssistantMode, AssistantTurn
from abc_fashion.model.catalogue import Style
from abc_fashion.model.user import Customer
from abc_fashion.view._util import SKY_300, body, guarded, log, run_in_thread


class AssistantFrm(tk.Toplevel):
    def __init__(self, customer: Customer | None, style: Style):
        super().__init__()
        self.customer = customer
        self.style = style
        self.list_turn: list[AssistantTurn] = []
        self.catalogue_controller = CatalogueController()
        self._build()
        self._append("Trợ lý", f"Xin chào! Bạn muốn hỏi gì về \"{style.name}\"? "
                               "(giá, tồn kho, chất liệu, cỡ, bảo quản, đổi trả)")
        if customer is not None:
            self.list_turn = self.catalogue_controller.get_assistant_history(customer, style)
            for t in self.list_turn:
                self._append("Bạn", t.question)
                self._append("Trợ lý", t.answer)

    def _build(self) -> None:
        f = body(self, f"Trợ lý — {self.style.name}")
        self.txa_conversation = tk.Text(f, height=20, width=72, wrap="word", state="disabled")
        self.txa_conversation.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.txa_conversation.tag_configure("who", font="AbcBold", foreground=SKY_300)
        self.txt_question = ttk.Entry(f, width=60)
        self.txt_question.grid(row=1, column=0, sticky="we", pady=6)
        self.txt_question.bind("<Return>", lambda e: self.on_ask())
        self.btn_ask = ttk.Button(f, text="Hỏi", command=self.on_ask)
        self.btn_ask.grid(row=1, column=1, padx=4)
        self.lbl_mode = ttk.Label(f, text="", style="Muted.TLabel")
        self.lbl_mode.grid(row=1, column=2)
        f.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)
        self.txt_question.focus_set()

    def _append(self, who: str, text: str) -> None:
        self.txa_conversation.config(state="normal")
        self.txa_conversation.insert("end", f"{who}: ", "who")
        self.txa_conversation.insert("end", f"{text}\n\n")
        self.txa_conversation.config(state="disabled")
        self.txa_conversation.see("end")

    @guarded
    def on_ask(self) -> None:
        question = self.txt_question.get().strip()
        if not question:
            return
        self.txt_question.delete(0, "end")
        self.btn_ask.state(["disabled"])
        self.lbl_mode.config(text="đang trả lời…")
        started = time.perf_counter()

        self._append("Bạn", question)           # luồng phụ chỉ gọi gateway, không chạm widget / CSDL
        run_in_thread(self, lambda: self.catalogue_controller.ask_assistant(question, self.style),
                      lambda result: self._on_answer(result, started))

    @guarded
    def _on_answer(self, result, started: float) -> None:
        self.btn_ask.state(["!disabled"])
        if isinstance(result, Exception):
            log.error("AssistantEngine.ask: %s", result)
            self.lbl_mode.config(text="lỗi")
            return self._append("Trợ lý", "Xin lỗi, trợ lý đang gặp sự cố. Bạn thử lại sau nhé.")
        self._append("Trợ lý", result["answer"])
        self.lbl_mode.config(text="AI" if result["mode"] == AssistantMode.MODEL else "cơ bản")
        self.list_turn.append(self.catalogue_controller.save_assistant_turn(
            self.customer, self.style, result, int((time.perf_counter() - started) * 1000)))
