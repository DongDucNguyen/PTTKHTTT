"""UserDAO — Tài khoản đăng nhập của mọi loại người dùng (khách, nhân viên, nhà cung cấp)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _check_password, _hash_password, _is_hashed, _like, _to_entity
from abc_fashion.model.user import AccountStatus, User


class UserDAO(DAO):
    """Bảng tblUser. Dùng bởi: EditAccountFrm, LoginFrm, SearchAccountFrm."""

    def check_login(self, user: User) -> bool:
        row = self.con.execute(
            'SELECT "id","password","status","created_at","last_login_at" FROM "tblUser" '
            'WHERE lower("email") = lower(%s)', (user.email,)).fetchone()
        if row is None or not _check_password(user.password or "", row["password"]):
            return False
        if row["status"] != AccountStatus.ACTIVE.value:
            return False
        if not _is_hashed(row["password"]):            # mục 13 #15: băm lại mật khẩu bản rõ cũ
            self.con.execute('UPDATE "tblUser" SET "password" = %s WHERE "id" = %s',
                             (_hash_password(user.password), row["id"]))
        user.id, user.status = row["id"], AccountStatus(row["status"])
        user.created_at, user.last_login_at = row["created_at"], row["last_login_at"]
        self.con.execute('UPDATE "tblUser" SET "last_login_at" = now() WHERE "id" = %s', (user.id,))
        user.password = None                            # không giữ mật khẩu trong bộ nhớ phiên
        return True

    def search_user(self, key: str, user_type: str, status: str) -> list[User]:
        k = _like(key)
        rows = self.con.execute(
            'SELECT u."id", u."email", u."status", u."created_at", u."last_login_at", '
            '  coalesce(c."full_name", s."full_name", p."name") AS full_name, '
            '  CASE WHEN c."id" IS NOT NULL THEN \'customer\' WHEN s."id" IS NOT NULL THEN \'staff\' '
            '       WHEN p."id" IS NOT NULL THEN \'supplier\' ELSE \'\' END AS user_type, '
            '  s."role" AS role '
            'FROM "tblUser" u '
            'LEFT JOIN "tblCustomer" c ON c."userId" = u."id" '
            'LEFT JOIN "tblStaffMember" s ON s."userId" = u."id" '
            'LEFT JOIN "tblSupplier" p ON p."userId" = u."id" '
            'WHERE (u."email" ILIKE %s OR c."full_name" ILIKE %s OR s."full_name" ILIKE %s OR p."name" ILIKE %s) '
            '  AND (%s::text = \'\' OR (%s::text = \'customer\' AND c."id" IS NOT NULL) '
            '       OR (%s::text = \'staff\' AND s."id" IS NOT NULL) OR (%s::text = \'supplier\' AND p."id" IS NOT NULL)) '
            '  AND (%s::text = \'\' OR u."status" = %s::text) '
            'ORDER BY u."email"',
            (k, k, k, k, user_type or "", user_type or "", user_type or "", user_type or "",
             status or "", status or "")).fetchall()
        return [_to_entity(User, r) for r in rows]

    def update_user_status(self, user: User) -> bool:
        n = self.con.execute('UPDATE "tblUser" SET "status" = %s WHERE "id" = %s',
                             (user.status.value, user.id)).rowcount
        return n == 1

    def reset_password(self, user: User) -> bool:
        n = self.con.execute('UPDATE "tblUser" SET "password" = %s WHERE "id" = %s',
                             (_hash_password(user.password), user.id)).rowcount
        return n == 1

    def is_email_used(self, email: str) -> bool:
        return self.con.execute('SELECT 1 FROM "tblUser" WHERE lower("email") = lower(%s)',
                                (email.strip(),)).fetchone() is not None
