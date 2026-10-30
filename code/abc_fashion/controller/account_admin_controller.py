"""AccountAdminController — quản trị tài khoản và nhật ký thay đổi (UC20)."""
from __future__ import annotations

import secrets
from datetime import date

from abc_fashion.control.dao.audit_log_entry_dao import AuditLogEntryDAO
from abc_fashion.control.dao.staff_member_dao import StaffMemberDAO
from abc_fashion.control.dao.user_dao import UserDAO
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.audit import AuditAction, AuditLogEntry
from abc_fashion.model.user import AccountStatus, StaffRole, StaffMember, User


class AccountAdminController:
    def __init__(self):
        self.user_dao = UserDAO()
        self.staff_member_dao = StaffMemberDAO()
        self.audit_log_entry_dao = AuditLogEntryDAO()

    def search_user(self, key: str, user_type: str, status: AccountStatus | None) -> list[User]:
        return self.user_dao.search_user(key or "", user_type or "", status.value if status else "")

    def get_staff_member(self, user: User) -> StaffMember | None:
        """Hồ sơ nhân viên của tài khoản (None nếu không phải nhân viên)."""
        if getattr(user, "user_type", "") != "staff":
            return None
        return self.staff_member_dao.get_staff_member_by_user(user)

    def get_all_staff(self) -> list[StaffMember]:
        return self.staff_member_dao.get_all_staff_member()

    def _log(self, staff: StaffMember, user: User, action: AuditAction, changes: str) -> None:
        self.audit_log_entry_dao.add_audit_log_entry(
            AuditLogEntry(entity=f"tblUser#{user.id}", action=action, changes=changes), staff)

    def suspend_account(self, staff: StaffMember, user: User) -> bool:
        if user.id == staff.userId:
            raise BusinessError("Không thể tự khoá tài khoản của chính mình")
        user.status = AccountStatus.SUSPENDED
        ok = self.user_dao.update_user_status(user)
        if ok:
            self._log(staff, user, AuditAction.SUSPEND_ACCOUNT, "status: active -> suspended")
        return ok

    def activate_account(self, staff: StaffMember, user: User) -> bool:
        user.status = AccountStatus.ACTIVE
        ok = self.user_dao.update_user_status(user)
        if ok:
            self._log(staff, user, AuditAction.UPDATE, "status: suspended -> active")
        return ok

    def reset_password(self, staff: StaffMember, user: User) -> str | None:
        """Đặt mật khẩu tạm ngẫu nhiên; trả mật khẩu tạm (chỉ hiện một lần) hoặc None nếu không đặt được."""
        temp = secrets.token_urlsafe(8)
        user.password = temp
        ok = self.user_dao.reset_password(user)
        user.password = None
        if not ok:
            return None
        self._log(staff, user, AuditAction.RESET_PASSWORD, "đặt lại mật khẩu tạm")
        return temp

    def change_role(self, staff: StaffMember, staff_member: StaffMember, role: StaffRole) -> bool:
        """Đổi vai trò nhân viên; trả False nếu vai trò không đổi."""
        if staff_member.id == staff.id:
            raise BusinessError("Không tự đổi vai trò của chính mình")
        old = staff_member.role
        if role is None or role == old:
            return False
        staff_member.role = role
        if not self.staff_member_dao.update_role(staff_member):
            staff_member.role = old
            return False
        self._log(staff, User(id=staff_member.userId), AuditAction.UPDATE, f"role: {old.value} -> {role.value}")
        return True

    def search_audit_log(self, start: date, end: date, staff: StaffMember | None,
                         action: AuditAction | None) -> list[AuditLogEntry]:
        if start > end:
            raise BusinessError("Ngày bắt đầu phải trước ngày kết thúc")
        return self.audit_log_entry_dao.search_audit_log_entry(start, end, staff, action)
