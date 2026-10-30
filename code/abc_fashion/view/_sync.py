"""Lên lịch tác vụ nền của ứng dụng desktop khi nối dịch vụ ngoài (chế độ http). Module riêng tư của view layer;
do `main.py` khởi động. Nghiệp vụ nằm ở SyncController; module này chỉ lo nhịp `after` của Tk và luồng phụ.

- ShipmentSync: cứ vài giây hỏi hãng vận chuyển về các kiện đang đi (luồng phụ), rồi ghi sự kiện, suy trạng thái
  đơn và báo khách (luồng giao diện).
- refresh_search_index / push_search_index: đẩy danh mục sản phẩm lên dịch vụ AI.

Quy tắc luồng (mục 11): luồng phụ chỉ gọi hàm "an toàn ở luồng phụ" của controller; mọi lời gọi chạm CSDL ở luồng
giao diện.
"""
from __future__ import annotations

import tkinter as tk

from abc_fashion.controller.sync_controller import SyncController
from abc_fashion.view._util import log, run_in_thread


class ShipmentSync:
    def __init__(self, root: tk.Misc, interval_ms: int = 3000):
        self.root, self.interval = root, interval_ms
        self.sync_controller = SyncController()
        self._running = False

    def start(self) -> None:
        self._running = True
        self.root.after(self.interval, self._tick)

    def stop(self) -> None:
        self._running = False

    def _again(self) -> None:
        if self._running:
            self.root.after(self.interval, self._tick)

    def _tick(self) -> None:
        if not self._running:
            return
        try:
            shipments = self.sync_controller.get_open_shipments()
        except Exception:                                   # noqa: BLE001 - CSDL tạm mất kết nối
            log.exception("ShipmentSync: đọc kiện")
            return self._again()
        if not shipments:
            return self._again()
        run_in_thread(self.root, lambda: self.sync_controller.fetch_tracking(shipments), self._apply)

    def _apply(self, results) -> None:
        if isinstance(results, Exception):
            log.warning("ShipmentSync: %s", results)
            return self._again()
        try:
            self.sync_controller.apply_tracking(results)
        except Exception:                                   # noqa: BLE001
            log.exception("ShipmentSync: ghi sự kiện")
        self._again()


def push_search_index(root: tk.Misc) -> None:
    """Đẩy danh mục sản phẩm lên dịch vụ AI (đọc CSDL ở luồng giao diện, gửi ở luồng phụ)."""
    SyncController().push_search_index()


def refresh_search_index(win: tk.Misc) -> None:
    """Sau khi sửa sản phẩm ngoài ProductController (vd. kiểm thử): cập nhật chỉ mục AI. Chỉ có tác dụng ở chế độ http."""
    push_search_index(win)
