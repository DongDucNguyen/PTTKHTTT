"""StaffMemberDAO — Hồ sơ nhân viên và vai trò."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity
from abc_fashion.model.user import StaffMember, User


class StaffMemberDAO(DAO):
    """Bảng tblStaffMember. Dùng bởi: EditAccountFrm, LoginFrm, AuditLogFrm."""

    def get_staff_member_by_user(self, user: User) -> StaffMember | None:
        row = self.con.execute(
            'SELECT s.*, u."email", u."status", u."created_at", u."last_login_at" '
            'FROM "tblStaffMember" s JOIN "tblUser" u ON u."id" = s."userId" WHERE s."userId" = %s',
            (user.id,)).fetchone()
        return _to_entity(StaffMember, row) if row else None

    def get_all_staff_member(self) -> list[StaffMember]:
        rows = self.con.execute('SELECT * FROM "tblStaffMember" ORDER BY "full_name"').fetchall()
        return [_to_entity(StaffMember, r) for r in rows]

    def update_role(self, staff: StaffMember) -> bool:
        n = self.con.execute('UPDATE "tblStaffMember" SET "role" = %s WHERE "id" = %s',
                             (staff.role.value, staff.id)).rowcount
        return n == 1
