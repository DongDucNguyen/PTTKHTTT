"""TrackShipmentFrm — Theo dõi kiện (UC11)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller.order_controller import OrderController
from abc_fashion.model.fulfilment import Shipment
from abc_fashion.view._util import body, fill_table, fmt_dt, guarded, info, label, make_table, watch


class TrackShipmentFrm(tk.Toplevel):
    def __init__(self, shipment: Shipment):
        super().__init__()
        self.shipment = shipment
        self.order_controller = OrderController()
        self._build()
        self._reload()
        watch(self, lambda: self.order_controller.get_shipment_signature(self.shipment),
              self._reload_from_db)                                   # kiện tự tiến trạng thái ở nền

    def _reload_from_db(self) -> None:
        self.shipment = self.order_controller.get_shipment(self.shipment)
        self._reload()

    def _build(self) -> None:
        f = body(self, f"Theo dõi kiện #{self.shipment.id}")
        self.lbl_carrier = ttk.Label(f)
        self.lbl_carrier.grid(row=0, column=0, sticky="w")
        self.lbl_tracking_no = ttk.Label(f)
        self.lbl_tracking_no.grid(row=1, column=0, sticky="w")
        self.lbl_status = ttk.Label(f, style="H3.TLabel")
        self.lbl_status.grid(row=2, column=0, sticky="w")
        self.tbl_shipment_record = make_table(f, [("sku", "SKU", 120), ("name", "Sản phẩm", 220), ("qty", "SL", 50)],
                                              height=3)
        self.tbl_shipment_record.box.grid(row=3, column=0, sticky="nsew", pady=6)
        self.tbl_shipment_event = make_table(f, [("time", "Thời điểm", 130), ("status", "Trạng thái", 130),
                                                 ("note", "Ghi chú", 260)], height=6)
        self.tbl_shipment_event.box.grid(row=4, column=0, sticky="nsew")
        self.btn_refresh = ttk.Button(f, text="Cập nhật từ hãng vận chuyển", command=self.on_refresh)
        self.btn_refresh.grid(row=5, column=0, sticky="e", pady=6)
        f.columnconfigure(0, weight=1)

    def _reload(self) -> None:
        s = self.shipment
        self.lbl_carrier.config(text=f"Hãng: {s.carrier or 'chưa bàn giao'}")
        self.lbl_tracking_no.config(text=f"Mã vận đơn: {s.tracking_no or '—'}")
        self.lbl_status.config(text=f"Trạng thái: {label(s.status)}"
                                    + (f" (giao lúc {fmt_dt(s.delivered_at)})" if s.delivered_at else ""))
        fill_table(self.tbl_shipment_record, [(r.id, (getattr(r, "sku", ""), getattr(r, "style_name", ""), r.quantity))
                                              for r in getattr(s, "records", [])])
        fill_table(self.tbl_shipment_event, [(e.id, (fmt_dt(e.occurred_at), label(e.status), e.note or ""))
                                             for e in self.order_controller.get_shipment_events(s)])
        self.btn_refresh.state(["!disabled"] if s.tracking_no else ["disabled"])

    @guarded
    def on_refresh(self) -> None:
        if not self.shipment.tracking_no:
            return
        added = self.order_controller.refresh_tracking(self.shipment)
        self._reload()
        if not added:
            info(self, "Chưa có cập nhật mới")
