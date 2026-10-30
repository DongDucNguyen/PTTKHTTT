"""NotificationDAO — Thông báo gửi khách (e-mail / SMS / app)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _val
from abc_fashion.model.customer_data import Notification
from abc_fashion.model.user import Customer


class NotificationDAO(DAO):
    """Bảng tblNotification. Dùng bởi: CheckoutFrm, ManageOrderFrm, ProcessReturnFrm, ConfirmOrderFrm."""

    def _get_recipient(self, customer_id: int) -> tuple[str | None, str | None]:
        """(e-mail, điện thoại) của khách — để view gắn `notification.recipient` cho dịch vụ e-mail / SMS."""
        row = self.con.execute('SELECT u."email", c."phone" FROM "tblCustomer" c JOIN "tblUser" u ON u."id" = c."userId" '
                               'WHERE c."id" = %s', (customer_id,)).fetchone()
        return (row["email"], row["phone"]) if row else (None, None)

    def add_notification(self, notification: Notification, customer: Customer) -> bool:
        row = self.con.execute(
            'INSERT INTO "tblNotification"("channel","event_type","message","status","sent_at","customerId") '
            'VALUES (%s,%s,%s,%s,%s,%s) RETURNING "id"',
            (_val(notification.channel), _val(notification.event_type), (notification.message or "")[:1000],
             _val(notification.status), notification.sent_at, customer.id)).fetchone()
        notification.id, notification.customerId = row["id"], customer.id
        return True
