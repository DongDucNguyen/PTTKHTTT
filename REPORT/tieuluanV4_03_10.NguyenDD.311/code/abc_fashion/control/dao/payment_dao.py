# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.payment_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.sales import tblOrder, tblPayment


class PaymentDAO(DAO):
    """PaymentDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblPayment
    """

    def add_payment(self, payment: tblPayment, order: tblOrder):
        raise NotImplementedError

    def update_payment(self, payment: tblPayment):
        raise NotImplementedError

    def get_payment_by_order(self, order: tblOrder):
        raise NotImplementedError
