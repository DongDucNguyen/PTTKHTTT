# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.saved_size_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.customer_data import tblSavedSize
from abc_fashion.model.user import tblCustomer


class SavedSizeDAO(DAO):
    """SavedSizeDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblSavedSize
    """

    def get_saved_size_by_customer(self, customer: tblCustomer):
        raise NotImplementedError

    def save_saved_size(self, size: tblSavedSize, customer: tblCustomer):
        raise NotImplementedError
