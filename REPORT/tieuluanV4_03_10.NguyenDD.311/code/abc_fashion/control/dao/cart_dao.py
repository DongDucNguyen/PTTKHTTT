# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.cart_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.sales import tblCart, tblCartItem
from abc_fashion.model.user import tblCustomer


class CartDAO(DAO):
    """CartDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblCart
    """

    def get_cart_by_customer(self, customer: tblCustomer):
        raise NotImplementedError

    def add_cart_item(self, cart: tblCart, item: tblCartItem):
        raise NotImplementedError

    def update_cart_item(self, item: tblCartItem):
        raise NotImplementedError

    def delete_cart_item(self, item: tblCartItem):
        raise NotImplementedError

    def clear_cart(self, cart: tblCart):
        raise NotImplementedError
