"""NotificationGateway — Email/SMS Service.

Chế độ `sandbox` (mặc định): ghi ra file nhật ký. Chế độ `http`: gửi tới dịch vụ e-mail / SMS mô phỏng
(external_services/notify, cổng 8103); xem thư đã gửi ở http://127.0.0.1:8103/inbox.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

from abc_fashion.control.gateway import _http
from abc_fashion.model.customer_data import Notification

OUTBOX = os.environ.get("ABC_FASHION_OUTBOX",
                        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                            os.path.abspath(__file__))))), "outbox.log"))

log = logging.getLogger(__name__)


class NotificationGateway:
    """Dùng bởi: CheckoutFrm, ManageOrderFrm, ProcessReturnFrm, EditRestockRequestFrm."""

    def send(self, notification: Notification) -> bool:
        """Gửi `notification.message` qua `notification.channel`. `True` = đã gửi.

        Chế độ http cần địa chỉ nhận: view gắn `notification.recipient` (e-mail hoặc điện thoại) trước khi gọi.
        """
        if _http.use_http():
            to = getattr(notification, "recipient", None)
            if not to:
                log.warning("Thông báo %s không có người nhận", notification.event_type)
                return False
            try:
                status, _ = _http.call("notify", "POST", "/v1/messages", {
                    "channel": notification.channel.value, "to": to, "event_type": notification.event_type.value,
                    "body": notification.message, "client_ref": str(notification.customerId or "")})
            except _http.GatewayUnavailable as e:                 # lỗi gửi không được chặn nghiệp vụ
                log.warning("Notify: %s", e)
                return False
            return status == 202
        try:
            with open(OUTBOX, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}\t{notification.channel.value}\t"
                        f"customer={notification.customerId}\t{notification.event_type.value}\t{notification.message}\n")
            return True
        except OSError as e:
            log.warning("Không ghi được outbox: %s", e)
            return False
