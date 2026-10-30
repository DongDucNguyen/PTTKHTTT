"""PaymentMethodDAO — Phương thức thanh toán đã liên kết (chỉ lưu số đã che)."""
from __future__ import annotations

import psycopg

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.customer_data import PaymentMethod
from abc_fashion.model.user import Customer


class PaymentMethodDAO(DAO):
    """Bảng tblPaymentMethod. Dùng bởi: CheckoutFrm, ConfirmOrderFrm, LinkPaymentMethodFrm, ProfileFrm."""

    def get_payment_method_by_customer(self, customer: Customer) -> list[PaymentMethod]:
        rows = self.con.execute(
            'SELECT * FROM "tblPaymentMethod" WHERE "customerId" = %s ORDER BY "is_default" DESC, "id"',
            (customer.id,)).fetchall()
        return [_to_entity(PaymentMethod, r) for r in rows]

    def add_payment_method(self, method: PaymentMethod, customer: Customer) -> bool:
        masked = method.masked_number or ""
        if "*" not in masked or sum(ch.isdigit() for ch in masked) > 4:     # NFR04: không lưu số đầy đủ
            return False
        with self.con.transaction():
            count = self.con.execute('SELECT count(*) AS n FROM "tblPaymentMethod" WHERE "customerId" = %s',
                                     (customer.id,)).fetchone()["n"]
            method.is_default = bool(method.is_default) or count == 0
            if method.is_default:
                self.con.execute('UPDATE "tblPaymentMethod" SET "is_default" = false WHERE "customerId" = %s',
                                 (customer.id,))
            row = self.con.execute(
                'INSERT INTO "tblPaymentMethod"("provider","method_type","masked_number","is_default","customerId") '
                'VALUES (%s,%s,%s,%s,%s) RETURNING "id"',
                (method.provider, method.method_type.value, masked, method.is_default, customer.id)).fetchone()
        method.id, method.customerId = row["id"], customer.id
        return True

    def delete_payment_method(self, method: PaymentMethod) -> bool:
        try:
            with self.con.transaction():
                row = self.con.execute('DELETE FROM "tblPaymentMethod" WHERE "id" = %s RETURNING "is_default","customerId"',
                                       (method.id,)).fetchone()
                if row and row["is_default"]:     # chuyển mặc định sang phương thức còn lại đầu tiên
                    self.con.execute(
                        'UPDATE "tblPaymentMethod" SET "is_default" = true WHERE "id" = '
                        '(SELECT min("id") FROM "tblPaymentMethod" WHERE "customerId" = %s)', (row["customerId"],))
        except psycopg.errors.ForeignKeyViolation:
            return False                          # đã dùng trong Payment
        return row is not None
