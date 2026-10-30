"""PaymentDAO — Các lần thu (`charge`) và hoàn (`refund`) của đơn."""
from __future__ import annotations

from abc_fashion.control.dao.dao import BUSINESS_ERRORS, DAO, _to_entity, _val
from abc_fashion.model.sales import PaymentStatus, Order, Payment


class PaymentDAO(DAO):
    """Bảng tblPayment. Dùng bởi: CheckoutFrm, ConfirmOrderFrm, ManageOrderFrm, ProcessReturnFrm."""

    def add_payment(self, payment: Payment, order: Order) -> bool:
        try:
            with self.con.transaction():
                row = self.con.execute(
                    'INSERT INTO "tblPayment"("kind","method","amount","status","transaction_ref","created_at",'
                    '"orderId","paymentMethodId") VALUES (%s,%s,%s,%s,%s,now(),%s,%s) RETURNING "id","created_at"',
                    (_val(payment.kind), _val(payment.method), payment.amount, _val(payment.status),
                     payment.transaction_ref, order.id, payment.paymentMethodId)).fetchone()
        except BUSINESS_ERRORS:
            return False
        payment.id, payment.created_at, payment.orderId = row["id"], row["created_at"], order.id
        return True

    def update_payment(self, payment: Payment) -> bool:
        """Idempotent: chỉ đổi lần thanh toán còn `pending`."""
        n = self.con.execute(
            'UPDATE "tblPayment" SET "status" = %s, "transaction_ref" = coalesce(%s, "transaction_ref") '
            'WHERE "id" = %s AND "status" = %s',
            (_val(payment.status), payment.transaction_ref, payment.id, PaymentStatus.PENDING.value)).rowcount
        return n == 1

    def get_payment_by_order(self, order: Order) -> list[Payment]:
        rows = self.con.execute(
            'SELECT p.*, m."masked_number", m."provider" FROM "tblPayment" p '
            'LEFT JOIN "tblPaymentMethod" m ON m."id" = p."paymentMethodId" '
            'WHERE p."orderId" = %s ORDER BY p."created_at", p."id"', (order.id,)).fetchall()
        return [_to_entity(Payment, r) for r in rows]
