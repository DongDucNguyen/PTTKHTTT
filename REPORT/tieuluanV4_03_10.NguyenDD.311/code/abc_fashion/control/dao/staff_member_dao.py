# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.staff_member_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.user import tblStaffMember, tblUser


class StaffMemberDAO(DAO):
    """StaffMemberDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblStaffMember
    """

    def get_staff_member_by_user(self, user: tblUser):
        raise NotImplementedError

    def get_all_staff_member(self):
        raise NotImplementedError

    def update_role(self, staff: tblStaffMember):
        raise NotImplementedError
