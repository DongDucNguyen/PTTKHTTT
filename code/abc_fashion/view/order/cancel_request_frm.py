"""CancelRequestFrm — Huỷ đơn / gửi yêu cầu huỷ (UC10)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.order_controller import OrderController
from abc_fashion.model.sales import OrderStatus, Order
from abc_fashion.view._util import body, button_row, confirm, guarded, info, label, message_label, warn

REASONS = ["Đổi ý, không muốn mua nữa", "Muốn đổi sản phẩm / cỡ khác", "Tìm được giá tốt hơn",
           "Đặt nhầm địa chỉ", "Giao hàng quá lâu", "Khác"]


class CancelRequestFrm(tk.Toplevel):
    def __init__(self, order: Order):
        super().__init__()
        self.order = order
        self.order_controller = OrderController()
        self._build()

    def _build(self) -> None:
        f = body(self, "Huỷ đơn")
        self.lbl_order_no = ttk.Label(f, text=f"Đơn {self.order.order_no} — {label(self.order.status)}",
                                      style="H3.TLabel")
        self.lbl_order_no.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ttk.Label(f, text="Lý do").grid(row=1, column=0, sticky="w")
        self.cbo_reason = ttk.Combobox(f, values=REASONS, state="readonly", width=40)
        self.cbo_reason.grid(row=1, column=1, sticky="w")
        self.cbo_reason.bind("<<ComboboxSelected>>", lambda e: self._toggle_detail())
        ttk.Label(f, text="Chi tiết").grid(row=2, column=0, sticky="w")
        self.txt_reason_detail = ttk.Entry(f, width=43, state="disabled")
        self.txt_reason_detail.grid(row=2, column=1, sticky="w", pady=3)
        if self.order.status == OrderStatus.PROCESSING:
            note = "Đơn đang được đóng gói: yêu cầu huỷ sẽ chờ quản lý duyệt."
        else:
            note = "Đơn sẽ được huỷ ngay; tiền đã thanh toán sẽ được hoàn lại."
        ttk.Label(f, text=note, style="Muted.TLabel").grid(row=3, column=0, columnspan=2, sticky="w", pady=4)
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=4, column=0, columnspan=2, sticky="w")
        self.btn_back = ttk.Button(f, text="Quay lại", command=self.on_back)
        self.btn_send = ttk.Button(f, text="Gửi", command=self.on_send)
        button_row(f, [self.btn_back, self.btn_send], 5)

    def _toggle_detail(self) -> None:
        self.txt_reason_detail.config(state="normal" if self.cbo_reason.get() == "Khác" else "disabled")

    @guarded
    def on_send(self) -> None:
        reason = self.cbo_reason.get()
        if reason == "Khác":
            reason = self.txt_reason_detail.get().strip()
        o = self.order
        if (reason and o.status in (OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED)
                and not confirm(self, f"Huỷ đơn {o.order_no}?")):
            return
        message, warning = self.order_controller.cancel_order(o, reason)
        if warning:
            warn(self, warning)
        info(self, message)
        self.destroy()

    def on_back(self) -> None:
        self.destroy()
