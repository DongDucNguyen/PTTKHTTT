# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.restock_request_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.inventory import tblRestockRequest
from abc_fashion.model.user import tblStaffMember, tblSupplier


class RestockRequestDAO(DAO):
    """RestockRequestDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblRestockRequest
    """

    def search_restock_request(self, status: str | None, supplier: tblSupplier | None):
        raise NotImplementedError

    def get_restock_request_detail(self, request: tblRestockRequest):
        raise NotImplementedError

    def add_restock_request(self, request: tblRestockRequest, staff: tblStaffMember):
        raise NotImplementedError

    def update_restock_request(self, request: tblRestockRequest):
        raise NotImplementedError

    def receive_restock_request(self, request: tblRestockRequest, staff: tblStaffMember):
        raise NotImplementedError
