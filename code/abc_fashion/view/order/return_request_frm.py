"""ReturnRequestFrm — Yêu cầu trả / đổi hàng (UC14)."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, ttk

from abc_fashion.controller.return_controller import ReturnController
from abc_fashion.model.returns import Resolution, ReturnReason, ReturnType, ReturnEvidence, ReturnRequest
from abc_fashion.model.sales import Order
from abc_fashion.model.user import Customer
from abc_fashion.view._util import (ChoiceBox, body, enum_choices, fill_table, guarded, info, label, make_table,
                                    message_label, read_file, selected, show, text_get, warn)


class ReturnRequestFrm(tk.Toplevel):
    def __init__(self, customer: Customer, order: Order):
        super().__init__()
        self.customer = customer
        self.order = order
        self.return_controller = ReturnController()
        self.return_request = ReturnRequest(orderId=order.id)
        self.return_request.items = []
        self.list_evidence: list[ReturnEvidence] = []
        self._build()
        fill_table(self.tbl_order_item, [(i.id, (i.sku, i.style_name, f"{i.colour}/{i.size_label}", i.quantity))
                                         for i in order.items])

    def _build(self) -> None:
        f = body(self, f"Trả / đổi hàng — {self.order.order_no}")
        ttk.Label(f, text="Hàng đã mua").grid(row=0, column=0, sticky="w")
        self.tbl_order_item = make_table(f, [("sku", "SKU", 100), ("name", "Sản phẩm", 200), ("var", "Màu / cỡ", 80),
                                             ("qty", "Đã mua", 60)], height=4)
        self.tbl_order_item.box.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.tbl_order_item.bind("<<TreeviewSelect>>", lambda e: self._load_replacements())
        bar = ttk.Frame(f)
        bar.grid(row=2, column=0, columnspan=3, sticky="w", pady=4)
        ttk.Label(bar, text="Số lượng trả").pack(side="left")
        self.spn_quantity = ttk.Spinbox(bar, from_=1, to=99, width=5)
        self.spn_quantity.set(1)
        self.spn_quantity.pack(side="left", padx=4)
        ttk.Label(bar, text="Đổi sang").pack(side="left", padx=(8, 0))
        self.cbo_replacement = ChoiceBox(bar, width=24)
        self.cbo_replacement.pack(side="left", padx=4)
        ttk.Button(bar, text="Thêm vào yêu cầu", command=self.on_select_item).pack(side="left", padx=4)
        ttk.Button(bar, text="Bỏ dòng", command=self._remove_item).pack(side="left")
        self.tbl_return_item = make_table(f, [("sku", "SKU", 100), ("qty", "SL trả", 60), ("rep", "Đổi sang", 160)],
                                          height=3)
        self.tbl_return_item.box.grid(row=3, column=0, columnspan=3, sticky="nsew")

        opt = ttk.Frame(f)
        opt.grid(row=4, column=0, columnspan=3, sticky="w", pady=6)
        self.var_return_type = tk.StringVar(value=ReturnType.RETURN.value)
        self.rdo_return_type = []
        ttk.Label(opt, text="Loại").grid(row=0, column=0, sticky="w")
        for c, t in enumerate(ReturnType):
            rb = ttk.Radiobutton(opt, text=label(t), value=t.value, variable=self.var_return_type,
                                 command=self._on_type)
            rb.grid(row=0, column=c + 1, sticky="w", padx=4)
            self.rdo_return_type.append(rb)
        ttk.Label(opt, text="Mong muốn").grid(row=1, column=0, sticky="w")
        self.var_desired_resolution = tk.StringVar(value=Resolution.REFUND.value)
        self.rdo_desired_resolution = []
        for c, r in enumerate(Resolution):
            rb = ttk.Radiobutton(opt, text=label(r), value=r.value, variable=self.var_desired_resolution)
            rb.grid(row=1, column=c + 1, sticky="w", padx=4)
            self.rdo_desired_resolution.append(rb)
        ttk.Label(opt, text="Lý do").grid(row=2, column=0, sticky="w")
        self.cbo_reason_code = ChoiceBox(opt, enum_choices(ReturnReason), width=22)
        self.cbo_reason_code.grid(row=2, column=1, columnspan=2, sticky="w")
        ttk.Label(f, text="Mô tả thêm").grid(row=5, column=0, sticky="w")
        self.txa_reason_detail = tk.Text(f, height=3, width=60, wrap="word")
        self.txa_reason_detail.grid(row=6, column=0, columnspan=3, sticky="we")
        ev = ttk.Frame(f)
        ev.grid(row=7, column=0, columnspan=3, sticky="we", pady=4)
        self.btn_add_evidence = ttk.Button(ev, text="Thêm ảnh / video bằng chứng", command=self.on_add_evidence)
        self.btn_add_evidence.pack(side="left")
        self.tbl_evidence = make_table(f, [("file", "Bằng chứng", 380), ("type", "Loại", 70)], height=3)
        self.tbl_evidence.box.grid(row=8, column=0, columnspan=3, sticky="nsew")
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=9, column=0, columnspan=2, sticky="w")
        self.btn_submit = ttk.Button(f, text="Gửi yêu cầu", command=self.on_submit)
        self.btn_submit.grid(row=9, column=2, sticky="e", pady=6)
        f.columnconfigure(0, weight=1)
        self._on_type()

    def _on_type(self) -> None:
        exchange = self.var_return_type.get() == ReturnType.EXCHANGE.value
        self.var_desired_resolution.set((Resolution.EXCHANGE if exchange else Resolution.REFUND).value)
        self.cbo_replacement.state(["!disabled"] if exchange else ["disabled"])
        self._load_replacements()

    def _load_replacements(self) -> None:
        item = selected(self.tbl_order_item, self.order.items)
        if item is None or self.var_return_type.get() != ReturnType.EXCHANGE.value:
            return self.cbo_replacement.set_choices([])
        self.cbo_replacement.set_choices([(f"{v.colour}/{v.size_label} (còn {v.available or 0})", v)
                                          for v in self.return_controller.get_replacement_options(item)])

    def _refresh_items(self) -> None:
        fill_table(self.tbl_return_item, [(i.orderItemId, (i.sku, i.quantity, getattr(i, "replacement_label", "")))
                                          for i in self.return_request.items])

    @guarded
    def on_select_item(self) -> None:
        item = selected(self.tbl_order_item, self.order.items)
        if item is None:
            return warn(self, "Chọn dòng hàng muốn trả")
        try:
            qty = int(self.spn_quantity.get())
        except ValueError:
            qty = 0
        ri = self.return_controller.make_return_item(item, qty, ReturnType(self.var_return_type.get()),
                                                     self.cbo_replacement.value())
        self.return_request.items = [i for i in self.return_request.items if i.orderItemId != item.id] + [ri]
        self._refresh_items()
        show(self.lbl_message, "")

    def _remove_item(self) -> None:
        sel = self.tbl_return_item.selection()
        if sel:
            self.return_request.items = [i for i in self.return_request.items if str(i.orderItemId) != sel[0]]
            self._refresh_items()

    @guarded
    def on_add_evidence(self) -> None:
        path = filedialog.askopenfilename(parent=self, title="Chọn ảnh / video",
                                          filetypes=[("Ảnh / video", "*.jpg *.jpeg *.png *.mp4 *.mov"), ("Tất cả", "*.*")])
        if not path:
            return
        e = self.return_controller.store_evidence(os.path.basename(path), read_file(path))
        e.id = len(self.list_evidence) + 1                       # khoá tạm cho bảng; xoá trước khi lưu
        self.list_evidence.append(e)
        fill_table(self.tbl_evidence, [(x.id, (x.file_name, label(x.media_type))) for x in self.list_evidence])

    @guarded
    def on_submit(self) -> None:
        rr = self.return_request
        rr.return_type = ReturnType(self.var_return_type.get())
        rr.desired_resolution = Resolution(self.var_desired_resolution.get())
        rr.reason_code, rr.reason_detail = self.cbo_reason_code.value(), text_get(self.txa_reason_detail)
        self.return_controller.submit_return_request(self.customer, self.order, rr, self.list_evidence)
        info(self, f"Đã gửi yêu cầu {rr.return_no}. Bộ phận chăm sóc khách hàng sẽ phản hồi sớm.")
        self.destroy()
