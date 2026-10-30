"""OrderDetailFrm — Chi tiết đơn và các hành động sau mua (UC09–UC14)."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from abc_fashion.controller._errors import AccessDenied
from abc_fashion.controller.order_controller import OrderController
from abc_fashion.model.sales import OrderStatus, Order
from abc_fashion.model.user import Customer
from abc_fashion.view._util import (body, confirm, fill_table, fmt_dt, guarded, label, make_table, modal, money,
                                    selected, ship_text, warn, watch)
from abc_fashion.view.order.cancel_request_frm import CancelRequestFrm
from abc_fashion.view.order.return_request_frm import ReturnRequestFrm
from abc_fashion.view.order.review_frm import ReviewFrm
from abc_fashion.view.order.track_shipment_frm import TrackShipmentFrm


class OrderDetailFrm(tk.Toplevel):
    def __init__(self, customer: Customer, order: Order):
        super().__init__()
        self.customer = customer
        self.order_controller = OrderController()
        self.order = order
        self._build()
        self._reload()
        watch(self, lambda: self.order_controller.get_order_signature(self.order), self._reload)   # vận chuyển ở nền

    def _build(self) -> None:
        f = body(self, "Chi tiết đơn hàng")
        head = ttk.Frame(f)
        head.grid(row=0, column=0, sticky="we")
        self.lbl_order_no = ttk.Label(head, style="H2.TLabel")
        self.lbl_order_no.grid(row=0, column=0, sticky="w")
        self.lbl_status = ttk.Label(head, style="H3.TLabel")
        self.lbl_status.grid(row=0, column=1, sticky="e", padx=20)
        self.lbl_placed_at = ttk.Label(head)
        self.lbl_placed_at.grid(row=1, column=0, columnspan=2, sticky="w")
        self.lbl_address = ttk.Label(head, wraplength=640)
        self.lbl_address.grid(row=2, column=0, columnspan=2, sticky="w")
        self.lbl_return = ttk.Label(head, style="Violet.TLabel")
        self.lbl_return.grid(row=3, column=0, columnspan=2, sticky="w")
        self.tbl_order_item = make_table(f, [("sku", "SKU", 100), ("name", "Sản phẩm", 200), ("var", "Màu / cỡ", 80),
                                             ("qty", "SL", 40), ("price", "Đơn giá", 90), ("disc", "Giảm", 80),
                                             ("total", "Thành tiền", 100), ("rev", "Đánh giá", 80)], height=5)
        self.tbl_order_item.box.grid(row=1, column=0, sticky="nsew", pady=6)
        self.tbl_order_item.bind("<<TreeviewSelect>>", lambda e: self._toggle_buttons())
        self.tbl_payment = make_table(f, [("kind", "Loại", 60), ("method", "Phương thức", 170), ("amount", "Số tiền", 100),
                                          ("status", "Trạng thái", 90), ("ref", "Mã giao dịch", 160),
                                          ("date", "Thời điểm", 120)], height=3)
        self.tbl_payment.box.grid(row=2, column=0, sticky="nsew")
        self.tbl_shipment = make_table(f, [("id", "Kiện", 50), ("dir", "Loại", 70), ("loc", "Kho", 110),
                                           ("carrier", "Hãng", 100), ("track", "Mã vận đơn", 110),
                                           ("status", "Trạng thái", 110), ("items", "Hàng", 200)], height=3)
        self.tbl_shipment.box.grid(row=3, column=0, sticky="nsew", pady=6)
        tot = ttk.Frame(f)
        tot.grid(row=4, column=0, sticky="e")
        self.lbl_subtotal, self.lbl_discount = ttk.Label(tot), ttk.Label(tot)
        self.lbl_shipping_fee, self.lbl_grand_total = ttk.Label(tot), ttk.Label(tot, style="H3.TLabel")
        for c, w in enumerate((self.lbl_subtotal, self.lbl_discount, self.lbl_shipping_fee, self.lbl_grand_total)):
            w.grid(row=0, column=c, padx=8)
        bar = ttk.Frame(f)
        bar.grid(row=5, column=0, sticky="e", pady=(8, 0))
        self.btn_track = ttk.Button(bar, text="Theo dõi kiện", command=self.on_track)
        self.btn_cancel_request = ttk.Button(bar, text="Huỷ đơn", command=self.on_cancel_request)
        self.btn_confirm_received = ttk.Button(bar, text="Đã nhận hàng", command=self.on_confirm_received)
        self.btn_review = ttk.Button(bar, text="Đánh giá dòng đã chọn", command=self.on_review)
        self.btn_return = ttk.Button(bar, text="Trả / đổi hàng", command=self.on_return)
        for b in (self.btn_track, self.btn_cancel_request, self.btn_confirm_received, self.btn_review, self.btn_return):
            b.pack(side="left", padx=3)
        f.columnconfigure(0, weight=1)

    def _reload(self) -> None:
        try:
            self.order = self.order_controller.get_order_detail(self.customer, self.order)      # NFR03
        except AccessDenied as e:
            messagebox.showerror("Không có quyền", str(e), parent=self)
            self.after(0, self.destroy)
            return
        o = self.order
        self.return_request = o.return_request
        self.lbl_order_no.config(text=f"Đơn {o.order_no}")
        self.lbl_status.config(text=label(o.status))
        self.lbl_placed_at.config(text=f"Đặt lúc {fmt_dt(o.placed_at)} · {label(o.delivery_service)}"
                                       + (f" · Ghi chú: {o.note}" if o.note else ""))
        self.lbl_address.config(text="Giao tới: " + ship_text(o))
        rr = self.return_request
        cancel_note = (f"Đã gửi yêu cầu huỷ: {o.cancel_reason}" if o.cancel_reason and o.status != OrderStatus.CANCELLED
                       else f"Lý do huỷ: {o.cancel_reason}" if o.cancel_reason else "")
        self.lbl_return.config(text=(f"Yêu cầu trả {rr.return_no}: {label(rr.status)}" if rr else cancel_note))
        fill_table(self.tbl_order_item, [(i.id, (i.sku, i.style_name, f"{i.colour}/{i.size_label}", i.quantity,
                                                 money(i.unit_price), money(i.discount), money(i.line_total),
                                                 "✓" if i.reviewed else "")) for i in o.items])
        fill_table(self.tbl_payment, [(p.id, (label(p.kind), label(p.method) + (f" {p.masked_number}"
                                                                                if getattr(p, "masked_number", None) else ""),
                                              money(p.amount), label(p.status), p.transaction_ref or "",
                                              fmt_dt(p.created_at))) for p in o.payments])
        fill_table(self.tbl_shipment, [(s.id, (s.id, label(s.direction), getattr(s, "location_name", ""), s.carrier or "",
                                               s.tracking_no or "", label(s.status),
                                               ", ".join(f"{r.sku}×{r.quantity}" for r in s.records)))
                                       for s in o.shipments])
        self.lbl_subtotal.config(text=f"Tạm tính {money(o.subtotal)}")
        self.lbl_discount.config(text=f"Giảm −{money(o.discount)}")
        self.lbl_shipping_fee.config(text=f"Phí ship {money(o.shipping_fee)}")
        self.lbl_grand_total.config(text=f"Tổng {money(o.grand_total)}")
        self._toggle_buttons()

    def _toggle_buttons(self) -> None:
        o = self.order
        item = selected(self.tbl_order_item, o.items)
        can = {self.btn_track: o.can_track, self.btn_cancel_request: o.can_cancel,
               self.btn_confirm_received: o.can_confirm_received,
               self.btn_review: item is not None and item.can_review, self.btn_return: o.can_return}
        for b, ok in can.items():
            b.state(["!disabled"] if ok else ["disabled"])

    @guarded
    def on_track(self) -> None:
        shipments = self.order.shipments
        s = selected(self.tbl_shipment, shipments) or (shipments[0] if len(shipments) == 1 else None)
        if s is None:
            return warn(self, "Chọn một kiện hàng")
        modal(TrackShipmentFrm(s), self)
        self._reload()

    @guarded
    def on_cancel_request(self) -> None:
        modal(CancelRequestFrm(self.order), self)
        self._reload()

    @guarded
    def on_confirm_received(self) -> None:
        if not confirm(self, "Xác nhận bạn đã nhận đủ hàng?"):
            return
        try:
            self.order_controller.confirm_received(self.order)                          # UC12
        finally:
            self._reload()

    @guarded
    def on_review(self) -> None:
        item = selected(self.tbl_order_item, self.order.items)
        if item is None:
            return warn(self, "Chọn dòng hàng muốn đánh giá")
        modal(ReviewFrm(self.customer, item), self)
        self._reload()

    @guarded
    def on_return(self) -> None:
        modal(ReturnRequestFrm(self.customer, self.order), self)
        self._reload()
