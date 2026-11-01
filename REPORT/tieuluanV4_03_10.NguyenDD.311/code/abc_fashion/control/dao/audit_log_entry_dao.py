# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.audit_log_entry_dao) -- do not edit the signatures.
from __future__ import annotations

from datetime import date, datetime

from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.audit import tblAuditLogEntry
from abc_fashion.model.user import tblStaffMember


class AuditLogEntryDAO(DAO):
    """AuditLogEntryDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblAuditLogEntry
    """

    def add_audit_log_entry(self, entry: tblAuditLogEntry, staff: tblStaffMember):
        raise NotImplementedError

    def search_audit_log_entry(self, start: date, end: date, staff: tblStaffMember | None, action: str | None):
        raise NotImplementedError
