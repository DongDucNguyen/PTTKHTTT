"""ProcessReturnFrm — Xử lý yêu cầu trả / đổi (UC18)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller._errors import BusinessError
from abc_fashion.controller.return_controller import ReturnController
from abc_fashion.model.catalogue import MediaType
from abc_fashion.model.returns import refund_amount, ReturnRequest
from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import (TEXT_500, body, confirm, fill_table, fmt_dt, guarded, info, label, make_table,
                                    message_label, money, open_media, show, show_image, text_get)

EVIDENCE_SIZE = (220, 180)


class ProcessReturnFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, return_request: ReturnRequest):
        super().__init__()
        self.staff = staff
        self.return_controller = ReturnController()
        self.return_request = return_request
        self._evidence_index = 0
        self._build()
        self._reload()

    def _build(self) -> None:
        f = body(self, "Xử lý trả / đổi hàng")
        info_box = ttk.Frame(f)
        info_box.grid(row=0, column=0, sticky="nw")
        self.lbl_return_no = ttk.Label(info_box, style="H2.TLabel")
        self.lbl_order_no, self.lbl_customer = ttk.Label(info_box), ttk.Label(info_box)
        self.lbl_return_type, self.lbl_reason = ttk.Label(info_box), ttk.Label(info_box, wraplength=420)
        self.lbl_status = ttk.Label(info_box, style="H3.TLabel")
        for r, w in enumerate((self.lbl_return_no, self.lbl_order_no, self.lbl_customer, self.lbl_return_type,
                               self.lbl_reason, self.lbl_status)):
            w.grid(row=r, column=0, sticky="w")
        self.cnv_evidence = tk.Canvas(f, width=EVIDENCE_SIZE[0], height=EVIDENCE_SIZE[1], highlightthickness=0)
        self.cnv_evidence.grid(row=0, column=1, sticky="ne", padx=(10, 0))
        self.cnv_evidence.bind("<Button-1>", lambda e: self._show_evidence(+1))
        self.cnv_evidence.bind("<Double-1>", lambda e: self._open_evidence())
        self.tbl_return_item = make_table(f, [("sku", "SKU", 110), ("name", "Sản phẩm", 180), ("qty", "SL trả", 50),
                                              ("price", "Đơn giá", 90), ("rep", "Đổi sang", 110),
                                              ("result", "Kiểm tra", 80), ("note", "Ghi chú kho", 160)], height=4)
        self.tbl_return_item.box.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=6)
        self.tbl_shipment = make_table(f, [("id", "Kiện", 50), ("dir", "Loại", 70), ("loc", "Kho", 110),
                                           ("track", "Mã vận đơn", 120), ("status", "Trạng thái", 110)], height=3)
        self.tbl_shipment.box.grid(row=2, column=0, columnspan=2, sticky="nsew")
        ttk.Label(f, text="Ghi chú quyết định").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.txa_decision_note = tk.Text(f, height=3, width=70, wrap="word")
        self.txa_decision_note.grid(row=4, column=0, columnspan=2, sticky="we")
        self.lbl_message = message_label(f)
        self.lbl_message.grid(row=5, column=0, columnspan=2, sticky="w")
        bar = ttk.Frame(f)
        bar.grid(row=6, column=0, columnspan=2, sticky="e", pady=6)
        self.btn_authorise = ttk.Button(bar, text="Duyệt", command=self.on_authorise)
        self.btn_reject = ttk.Button(bar, text="Từ chối", command=self.on_reject)
        self.btn_create_pickup = ttk.Button(bar, text="Tạo kiện lấy hàng", command=self.on_create_pickup)
        self.btn_refund = ttk.Button(bar, text="Hoàn tiền", command=self.on_refund)
        self.btn_ship_replacement = ttk.Button(bar, text="Gửi hàng đổi", command=self.on_ship_replacement)
        self.btn_close = ttk.Button(bar, text="Đóng yêu cầu", command=self.on_close)
        for b in (self.btn_authorise, self.btn_reject, self.btn_create_pickup, self.btn_refund,
                  self.btn_ship_replacement, self.btn_close):
            b.pack(side="left", padx=3)
        f.columnconfigure(0, weight=1)

    def _reload(self) -> None:
        self.return_request = r = self.return_controller.get_return_request_detail(self.return_request)
        self.lbl_return_no.config(text=f"Yêu cầu {r.return_no} · gửi {fmt_dt(r.requested_at)}")
        self.lbl_order_no.config(text=f"Đơn {getattr(r, 'order_no', '')} · giao lúc {fmt_dt(getattr(r, 'delivered_at', None))}")
        self.lbl_customer.config(text=f"Khách: {getattr(r, 'customer_name', '')} ({getattr(r, 'customer_email', '')})")
        self.lbl_return_type.config(text=f"{label(r.return_type)} · mong muốn: {label(r.desired_resolution)}")
        self.lbl_reason.config(text=f"Lý do: {label(r.reason_code)}" + (f" — {r.reason_detail}" if r.reason_detail else ""))
        self.lbl_status.config(text=f"Trạng thái: {label(r.status)}" + (f" · {r.decision_note}" if r.decision_note else ""))
        fill_table(self.tbl_return_item, [(i.id, (i.sku, getattr(i, "style_name", ""), i.quantity, money(i.unit_price),
                                                  f"{i.replacement_colour}/{i.replacement_size}" if i.replacementVariantId
                                                  else "", label(i.inspection_result), i.inspection_note or ""))
                                          for i in r.items])
        fill_table(self.tbl_shipment, [(s.id, (s.id, label(s.direction), getattr(s, "location_name", ""),
                                               s.tracking_no or "", label(s.status))) for s in r.shipments])
        self._show_evidence(0)
        enabled = {self.btn_authorise: r.can_authorise, self.btn_reject: r.can_reject,
                   self.btn_create_pickup: r.can_create_pickup, self.btn_refund: r.can_refund,
                   self.btn_ship_replacement: r.can_ship_replacement, self.btn_close: r.can_close}
        for b, ok in enabled.items():
            b.state(["!disabled"] if ok else ["disabled"])

    def _show_evidence(self, step: int) -> None:
        ev = getattr(self.return_request, "evidence", [])
        if not ev:
            self.cnv_evidence.delete("all")
            self.cnv_evidence.create_text(EVIDENCE_SIZE[0] // 2, EVIDENCE_SIZE[1] // 2, text="(không có bằng chứng)",
                                          fill=TEXT_500)
            return
        self._evidence_index = (self._evidence_index + step) % len(ev)
        item = ev[self._evidence_index]
        if item.media_type == MediaType.VIDEO:               # video bằng chứng: nhấp đúp mở bằng trình phát hệ thống
            self.cnv_evidence.delete("all")
            self.cnv_evidence.create_text(EVIDENCE_SIZE[0] // 2, EVIDENCE_SIZE[1] // 2, fill=TEXT_500, justify="center",
                                          text="▶ Video bằng chứng\n(nhấp đúp để mở)")
            return
        show_image(self.cnv_evidence, item.url, EVIDENCE_SIZE)

    def _open_evidence(self) -> None:
        ev = getattr(self.return_request, "evidence", [])
        if ev and ev[self._evidence_index % len(ev)].media_type == MediaType.VIDEO:
            if not open_media(ev[self._evidence_index % len(ev)].url):
                show(self.lbl_message, "Không mở được video bằng chứng")

    def _note(self) -> str:
        return text_get(self.txa_decision_note)

    def _do(self, action) -> None:
        """Gọi một thao tác của controller rồi nạp lại màn hình (cả khi lỗi nghiệp vụ, để thấy trạng thái mới nhất)."""
        try:
            action()
        except BusinessError:
            self._reload()
            raise
        self._reload()

    @guarded
    def on_authorise(self) -> None:
        def act():
            if not self.return_controller.authorise(self.staff, self.return_request, self._note()):
                info(self, "Đã quá hạn trả hàng — yêu cầu được tự động từ chối")             # UC18 E2
        self._do(act)

    @guarded
    def on_reject(self) -> None:
        self.return_controller.reject(self.staff, self.return_request, self._note())
        self._reload()

    @guarded
    def on_create_pickup(self) -> None:
        shipment = self.return_controller.create_pickup(self.staff, self.return_request)
        self._reload()
        info(self, f"Đã tạo kiện lấy hàng {shipment.tracking_no}")

    @guarded
    def on_refund(self) -> None:
        amount = refund_amount(self.return_request.items)
        question = (f"Hoàn {money(amount)} cho khách?" if amount > 0 else
                    "Không có dòng nào đạt kiểm tra nên không hoàn tiền. Đánh dấu đã xử lý (hoàn 0 đ)?")
        if not confirm(self, question):
            return
        self._do(lambda: self.return_controller.refund(self.staff, self.return_request, self._note()))

    @guarded
    def on_ship_replacement(self) -> None:
        self._do(lambda: self.return_controller.ship_replacement(self.staff, self.return_request, self._note()))

    @guarded
    def on_close(self) -> None:
        self._do(lambda: self.return_controller.close(self.staff, self.return_request, self._note()))
        info(self, "Đã đóng yêu cầu")
