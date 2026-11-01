# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.supplier_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.user import tblUser


class SupplierDAO(DAO):
    """SupplierDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblSupplier
    """

    def get_supplier_by_user(self, user: tblUser):
        raise NotImplementedError

    def get_all_supplier(self):
        raise NotImplementedError
