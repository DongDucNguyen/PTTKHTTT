# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.customer_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.user import tblCustomer, tblUser


class CustomerDAO(DAO):
    """CustomerDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblCustomer
    """

    def add_customer(self, customer: tblCustomer):
        raise NotImplementedError

    def get_customer_by_user(self, user: tblUser):
        raise NotImplementedError

    def update_customer(self, customer: tblCustomer):
        raise NotImplementedError
