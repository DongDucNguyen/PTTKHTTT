# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.payment_method_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.customer_data import tblPaymentMethod
from abc_fashion.model.user import tblCustomer


class PaymentMethodDAO(DAO):
    """PaymentMethodDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblPaymentMethod
    """

    def get_payment_method_by_customer(self, customer: tblCustomer):
        raise NotImplementedError

    def add_payment_method(self, method: tblPaymentMethod, customer: tblCustomer):
        raise NotImplementedError

    def delete_payment_method(self, method: tblPaymentMethod):
        raise NotImplementedError
