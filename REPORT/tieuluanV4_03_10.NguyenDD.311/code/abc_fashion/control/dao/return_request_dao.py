# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.return_request_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.returns import tblReturnItem, tblReturnRequest
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblStaffMember


class ReturnRequestDAO(DAO):
    """ReturnRequestDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblReturnRequest
    """

    def add_return_request(self, request: tblReturnRequest, order: tblOrder):
        raise NotImplementedError

    def get_return_request_by_order(self, order: tblOrder):
        raise NotImplementedError

    def search_return_request(self, key: str, status: str | None):
        raise NotImplementedError

    def get_return_request_detail(self, request: tblReturnRequest):
        raise NotImplementedError

    def update_return_request(self, request: tblReturnRequest, staff: tblStaffMember):
        raise NotImplementedError

    def update_return_item(self, item: tblReturnItem):
        raise NotImplementedError
