# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.gateway.payment_gateway) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.model.customer_data import tblPaymentMethod
from abc_fashion.model.sales import tblOrder, tblPayment
from abc_fashion.model.user import tblCustomer


class PaymentGateway:
    """PaymentGateway -- layer abc_fashion.control.gateway."""

    def charge(self, order: tblOrder, method: tblPaymentMethod):
        raise NotImplementedError

    def refund(self, payment: tblPayment):
        raise NotImplementedError

    def link_method(self, customer: tblCustomer, type: str, provider: str):
        raise NotImplementedError
