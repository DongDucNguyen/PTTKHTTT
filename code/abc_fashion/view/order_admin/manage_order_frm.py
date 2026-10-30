"""ManageOrderFrm — Xử lý đơn: chuyển trạng thái, huỷ, duyệt yêu cầu huỷ, hoàn tiền (UC22, UC23, UC10)."""
from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, ttk

from abc_fashion.controller._errors import BusinessError
from abc_fashion.controller.order_admin_controller import OrderAdminController
from abc_fashion.model.sales import OrderStatus, Order
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (ChoiceBox, body, confirm, fill_table, fmt_dt, guarded, info, label, make_table,
                                    message_label, money, selected_all, ship_text, show, warn, watch)


class ManageOrderFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, order: Order):
        super().__init__()
        self.staff = staff
        self.order_admin_controller = OrderAdminController()
        self.order = order
        self._build()
        self._reload()
        watch(self, lambda: self.order_admin_controller.get_order_signature(self.order), self._reload)

    def _build(self) -> None:
        f = body(self, "Xử lý đơn hàng")
        self.lbl_order_no = ttk.Label(f, style="H2.TLabel")
        self.lbl_order_no.grid(row=0, column=0, sticky="w")
        self.lbl_status = ttk.Label(f, style="H3.TLabel")
        self.lbl_status.grid(row=0, column=1, sticky="e")
        self.lbl_customer = ttk.Label(f, wraplength=700)
        self.lbl_customer.grid(row=1, column=0, columnspan=2, sticky="w")
        self.tbl_order_item = make_table(f, [("sku", "SKU", 100), ("name", "Sản phẩm", 200), ("qty", "SL", 40),
                                             ("price", "Đơn giá", 90), ("disc", "Giảm", 80), ("total", "Thành tiền", 100)],
                                         height=4)
        self.tbl_order_item.box.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=4)
        self.tbl_payment = make_table(f, [("kind", "Loại", 60), ("method", "Phương thức", 160), ("amount", "Số tiền", 100),
                                          ("status", "Trạng thái", 90), ("ref", "Mã giao dịch", 170),
                                          ("date", "Thời điểm", 120)], height=3)
        self.tbl_payment.box.grid(row=3, column=0, columnspan=2, sticky="nsew")
        ttk.Label(f, text="Kiện hàng (chọn kiện để giao một phần)").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.tbl_shipment = make_table(f, [("id", "Kiện", 50), ("dir", "Loại", 70), ("loc", "Kho", 110),
                                           ("carrier", "Hãng", 100), ("track", "Mã vận đơn", 110),
                                           ("status", "Trạng thái", 110), ("items", "Hàng", 200)], height=3,
                                       selectmode="extended")
        self.tbl_shipment.box.grid(row=5, column=0, columnspan=2, sticky="nsew")

        act = ttk.LabelFrame(f, text="Xử lý", padding=8)
        act.grid(row=6, column=0, columnspan=2, sticky="we", pady=8)
        ttk.Label(act, text="Chuyển sang").grid(row=0, column=0, sticky="w")
        self.cbo_new_status = ChoiceBox(act, width=20)
        self.cbo_new_status.grid(row=0, column=1, sticky="w", padx=4)
        self.btn_update_status = ttk.Button(act, text="Cập nhật trạng thái", command=self.on_update_status)
        self.btn_update_status.grid(row=0, column=2, padx=4)
        ttk.Label(act, text="Lý do huỷ").grid(row=1, column=0, sticky="w", pady=4)
        self.txt_cancel_reason = ttk.Entry(act, width=40)
        self.txt_cancel_reason.grid(row=1, column=1, sticky="w", padx=4)
        self.btn_cancel_order = ttk.Button(act, text="Huỷ đơn", command=self.on_cancel_order)
        self.btn_cancel_order.grid(row=1, column=2, padx=4)
        self.btn_approve_cancel_request = ttk.Button(act, text="Duyệt yêu cầu huỷ của khách",
                                                     command=self.on_approve_cancel_request)
        self.btn_approve_cancel_request.grid(row=2, column=1, sticky="w", padx=4)
        self.btn_refund = ttk.Button(act, text="Hoàn tiền…", command=self.on_refund)
        self.btn_refund.grid(row=2, column=2, padx=4)
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=7, column=0, columnspan=2, sticky="w")
        f.columnconfigure(0, weight=1)

    def _reload(self) -> None:
        self.order = self.order_admin_controller.get_order_detail(self.order)
        o = self.order
        self.lbl_order_no.config(text=f"Đơn {o.order_no} · {fmt_dt(o.placed_at)}")
        self.lbl_status.config(text=label(o.status))
        request = (f"  ·  KHÁCH YÊU CẦU HUỶ: {o.cancel_reason}" if o.cancel_reason and o.status != OrderStatus.CANCELLED
                   else (f"  ·  Lý do huỷ: {o.cancel_reason}" if o.cancel_reason else ""))
        self.lbl_customer.config(text=f"{getattr(o, 'customer_name', '')} ({getattr(o, 'customer_email', '')}) · "
                                      f"Giao: {ship_text(o)} · "
                                      f"{label(o.delivery_service)} · Tổng {money(o.grand_total)}{request}")
        fill_table(self.tbl_order_item, [(i.id, (i.sku, i.style_name, i.quantity, money(i.unit_price), money(i.discount),
                                                 money(i.line_total))) for i in o.items])
        fill_table(self.tbl_payment, [(p.id, (label(p.kind), label(p.method), money(p.amount), label(p.status),
                                              p.transaction_ref or "", fmt_dt(p.created_at))) for p in o.payments])
        fill_table(self.tbl_shipment, [(s.id, (s.id, label(s.direction), getattr(s, "location_name", ""), s.carrier or "",
                                               s.tracking_no or "", label(s.status),
                                               ", ".join(f"{r.sku}×{r.quantity}" for r in s.records)))
                                       for s in o.shipments])
        self.cbo_new_status.set_choices([(label(s), s) for s in o.next_statuses])
        for w, ok in ((self.btn_update_status, bool(o.next_statuses)), (self.btn_cancel_order, o.can_cancel),
                      (self.btn_approve_cancel_request, o.cancel_requested), (self.btn_refund, o.can_refund)):
            w.state(["!disabled"] if ok else ["disabled"])
        self.txt_cancel_reason.config(state="normal" if o.can_cancel else "disabled")

    @guarded
    def on_update_status(self) -> None:
        new = self.cbo_new_status.value()
        if new is None:
            return
        try:
            status = self.order_admin_controller.update_status(self.staff, self.order, new,
                                                               selected_all(self.tbl_shipment, self.order.shipments))
        except BusinessError:
            self._reload()
            raise
        self._reload()
        show(self.lbl_message, f"Đã chuyển sang {label(status)}", ok=True)

    @guarded
    def on_cancel_order(self) -> None:
        reason = self.txt_cancel_reason.get().strip()
        if not reason:
            return show(self.lbl_message, "Nhập lý do huỷ")
        self._cancel(reason)

    @guarded
    def on_approve_cancel_request(self) -> None:
        self._cancel(self.order.cancel_reason)

    def _cancel(self, reason: str) -> None:
        if not confirm(self, f"Huỷ đơn {self.order.order_no}? Hàng sẽ được trả về kho và tiền đã thu sẽ được hoàn."):
            return
        try:
            warning = self.order_admin_controller.cancel_order(self.staff, self.order, reason)
        except BusinessError:
            self._reload()
            raise
        if warning:
            warn(self, warning)
        self._reload()
        show(self.lbl_message, "Đã huỷ đơn", ok=True)

    @guarded
    def on_refund(self) -> None:
        paid = self.order.paid
        amount = simpledialog.askinteger("Hoàn tiền", f"Số tiền hoàn (tối đa {money(paid)}):", parent=self,
                                         initialvalue=paid, minvalue=1, maxvalue=paid)
        if not amount:
            return
        try:
            refunded = self.order_admin_controller.refund(self.staff, self.order, amount)
        finally:
            self._reload()
        info(self, f"Đã hoàn {money(refunded)}")
