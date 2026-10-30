"""AddressDAO — Sổ địa chỉ của khách."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.customer_data import Address
from abc_fashion.model.user import Customer


class AddressDAO(DAO):
    """Bảng tblAddress. Dùng bởi: CheckoutFrm, EditAddressFrm, ProfileFrm."""

    def get_address_by_customer(self, customer: Customer) -> list[Address]:
        rows = self.con.execute(
            'SELECT * FROM "tblAddress" WHERE "customerId" = %s ORDER BY "is_default" DESC, "id"',
            (customer.id,)).fetchall()
        return [_to_entity(Address, r) for r in rows]

    def add_address(self, address: Address, customer: Customer) -> bool:
        with self.con.transaction():
            count = self.con.execute('SELECT count(*) AS n FROM "tblAddress" WHERE "customerId" = %s',
                                     (customer.id,)).fetchone()["n"]
            address.is_default = bool(address.is_default) or count == 0     # địa chỉ đầu tiên luôn mặc định
            if address.is_default:
                self.con.execute('UPDATE "tblAddress" SET "is_default" = false WHERE "customerId" = %s',
                                 (customer.id,))
            row = self.con.execute(
                'INSERT INTO "tblAddress"("recipient_name","phone","street","ward","district","city",'
                '"is_default","customerId") VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING "id"',
                (address.recipient_name, address.phone, address.street, address.ward, address.district,
                 address.city, address.is_default, customer.id)).fetchone()
        address.id, address.customerId = row["id"], customer.id
        return True

    def update_address(self, address: Address) -> bool:
        with self.con.transaction():
            if address.is_default:
                self.con.execute('UPDATE "tblAddress" SET "is_default" = false WHERE "customerId" = %s AND "id" <> %s',
                                 (address.customerId, address.id))
            else:
                # không để khách mất địa chỉ mặc định: nếu bỏ mặc định của địa chỉ duy nhất thì giữ nguyên
                others = self.con.execute(
                    'SELECT count(*) AS n FROM "tblAddress" WHERE "customerId" = %s AND "id" <> %s AND "is_default"',
                    (address.customerId, address.id)).fetchone()["n"]
                if others == 0:
                    address.is_default = True
            n = self.con.execute(
                'UPDATE "tblAddress" SET "recipient_name"=%s,"phone"=%s,"street"=%s,"ward"=%s,"district"=%s,'
                '"city"=%s,"is_default"=%s WHERE "id"=%s',
                (address.recipient_name, address.phone, address.street, address.ward, address.district,
                 address.city, bool(address.is_default), address.id)).rowcount
        return n == 1

    def delete_address(self, address: Address) -> bool:
        with self.con.transaction():
            row = self.con.execute('SELECT "is_default","customerId" FROM "tblAddress" WHERE "id" = %s',
                                   (address.id,)).fetchone()
            if row is None:
                return False
            others = self.con.execute('SELECT count(*) AS n FROM "tblAddress" WHERE "customerId" = %s AND "id" <> %s',
                                      (row["customerId"], address.id)).fetchone()["n"]
            if row["is_default"] and others > 0:
                return False        # chọn địa chỉ mặc định khác trước
            self.con.execute('DELETE FROM "tblAddress" WHERE "id" = %s', (address.id,))
        return True
