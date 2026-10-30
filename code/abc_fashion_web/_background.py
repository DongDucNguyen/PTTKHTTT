"""Tác vụ nền của ứng dụng web khi nối dịch vụ ngoài (chế độ http) — tương đương `view/_sync.py` của desktop.

Một luồng nền với kết nối CSDL riêng: nhả đơn chờ thanh toán quá hạn (5 phút / lần), đồng bộ vận chuyển (3 giây / lần),
đẩy chỉ mục tìm kiếm lên dịch vụ AI khi khởi động. Nghiệp vụ nằm ở SyncController.
"""
from __future__ import annotations

import logging
import threading
import time

from abc_fashion.controller import _connection
from abc_fashion.controller.sync_controller import SyncController

log = logging.getLogger("abc_fashion")

SYNC_SECONDS = 3
EXPIRY_SECONDS = 5 * 60


def _loop() -> None:
    sync = SyncController()
    sync.push_search_index()
    next_expiry = 0.0
    while True:
        try:
            if time.monotonic() >= next_expiry:
                if (n := sync.release_expired_orders()):
                    log.info("Đã huỷ %d đơn chờ thanh toán quá hạn", n)
                next_expiry = time.monotonic() + EXPIRY_SECONDS
            shipments = sync.get_open_shipments()
            if shipments:
                sync.apply_tracking(sync.fetch_tracking(shipments))
        except Exception:                                   # noqa: BLE001 - CSDL / dịch vụ tạm lỗi: thử lại vòng sau
            log.exception("web background sync")
            _connection.release_connection()
        time.sleep(SYNC_SECONDS)


def start() -> None:
    threading.Thread(target=_loop, name="abc-web-sync", daemon=True).start()
    log.info("Chế độ gateway: http — đã bật đồng bộ vận chuyển nền cho web")
