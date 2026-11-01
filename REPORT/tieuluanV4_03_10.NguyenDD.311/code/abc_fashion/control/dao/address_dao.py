# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.address_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.customer_data import tblAddress
from abc_fashion.model.user import tblCustomer


class AddressDAO(DAO):
    """AddressDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblAddress
    """

    def get_address_by_customer(self, customer: tblCustomer):
        raise NotImplementedError

    def add_address(self, address: tblAddress, customer: tblCustomer):
        raise NotImplementedError

    def update_address(self, address: tblAddress):
        raise NotImplementedError

    def delete_address(self, address: tblAddress):
        raise NotImplementedError
