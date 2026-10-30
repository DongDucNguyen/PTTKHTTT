"""AuditLogEntryDAO — Nhật ký thay đổi của nhân viên."""
from __future__ import annotations

from datetime import date

from abc_fashion.control.dao.dao import DAO, _to_entity, _val
from abc_fashion.model.audit import AuditLogEntry
from abc_fashion.model.user import StaffMember


class AuditLogEntryDAO(DAO):
    """Bảng tblAuditLogEntry. Dùng bởi: AuditLogFrm, EditStyleFrm, EditAccountFrm, AdjustStockFrm, …"""

    def add_audit_log_entry(self, entry: AuditLogEntry, staff: StaffMember) -> bool:
        row = self.con.execute(
            'INSERT INTO "tblAuditLogEntry"("entity","action","changes","created_at","staffMemberId") '
            'VALUES (%s,%s,%s,now(),%s) RETURNING "id","created_at"',
            (entry.entity, _val(entry.action), (entry.changes or "")[:4000], staff.id)).fetchone()
        entry.id, entry.created_at, entry.staffMemberId = row["id"], row["created_at"], staff.id
        return True

    def search_audit_log_entry(self, start: date, end: date, staff: StaffMember | None,
                               action: str | None) -> list[AuditLogEntry]:
        staff_id = staff.id if staff else None
        action = _val(action) or None
        rows = self.con.execute(
            'SELECT a.*, s."full_name" AS staff_name FROM "tblAuditLogEntry" a '
            'JOIN "tblStaffMember" s ON s."id" = a."staffMemberId" '
            'WHERE a."created_at" >= %s::date AND a."created_at" < %s::date + 1 '
            '  AND (%s::int IS NULL OR a."staffMemberId" = %s::int) '
            '  AND (%s::text IS NULL OR a."action" = %s::text) '
            'ORDER BY a."created_at" DESC',
            (start, end, staff_id, staff_id, action, action)).fetchall()
        return [_to_entity(AuditLogEntry, r) for r in rows]
