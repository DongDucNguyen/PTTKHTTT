"""CustomerDAO — Hồ sơ khách hàng (lớp con của User)."""
from __future__ import annotations

import psycopg

from abc_fashion.control.dao.dao import DAO, _hash_password, _to_entity
from abc_fashion.model.user import AccountStatus, Customer, User


def _join_colours(colours: list[str] | None) -> str | None:
    if not colours:
        return None
    return ",".join(c.strip() for c in colours if c and c.strip())[:255] or None


def _split_colours(value: str | None) -> list[str]:
    return [c.strip() for c in (value or "").split(",") if c.strip()]


class CustomerDAO(DAO):
    """Bảng tblCustomer (+tblUser, tblCart khi đăng ký). Dùng bởi: ProfileFrm, RegisterFrm."""

    def add_customer(self, customer: Customer) -> bool:
        try:
            with self.con.transaction():
                u = self.con.execute(
                    'INSERT INTO "tblUser"("email","password","status","created_at") '
                    'VALUES (%s,%s,%s,now()) RETURNING "id","created_at"',
                    (customer.email.strip(), _hash_password(customer.password),
                     AccountStatus.ACTIVE.value)).fetchone()
                c = self.con.execute(
                    'INSERT INTO "tblCustomer"("full_name","phone","marketing_consent","preferred_colours","userId") '
                    'VALUES (%s,%s,%s,%s,%s) RETURNING "id"',
                    (customer.full_name, customer.phone, bool(customer.marketing_consent),
                     _join_colours(customer.preferred_colours), u["id"])).fetchone()
                self.con.execute('INSERT INTO "tblCart"("updated_at","subtotal","customerId") VALUES (now(),0,%s)',
                                 (c["id"],))
        except psycopg.errors.UniqueViolation:
            return False
        customer.id, customer.userId = c["id"], u["id"]
        customer.status, customer.created_at, customer.password = AccountStatus.ACTIVE, u["created_at"], None
        return True

    def get_customer_by_user(self, user: User) -> Customer | None:
        row = self.con.execute(
            'SELECT c.*, u."email", u."status", u."created_at", u."last_login_at" '
            'FROM "tblCustomer" c JOIN "tblUser" u ON u."id" = c."userId" WHERE c."userId" = %s',
            (user.id,)).fetchone()
        if row is None:
            return None
        customer = _to_entity(Customer, row)
        customer.preferred_colours = _split_colours(row["preferred_colours"])
        return customer

    def update_customer(self, customer: Customer) -> bool:
        n = self.con.execute(
            'UPDATE "tblCustomer" SET "full_name"=%s,"phone"=%s,"marketing_consent"=%s,"preferred_colours"=%s '
            'WHERE "id"=%s',
            (customer.full_name, customer.phone, bool(customer.marketing_consent),
             _join_colours(customer.preferred_colours), customer.id)).rowcount
        return n == 1
