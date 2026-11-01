# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.order_dao) -- do not edit the signatures.
from __future__ import annotations

from datetime import date, datetime

from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblCustomer


class OrderDAO(DAO):
    """OrderDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblOrder
    """

    def add_order(self, order: tblOrder, customer: tblCustomer):
        raise NotImplementedError

    def get_order_by_customer(self, customer: tblCustomer, status: str | None):
        raise NotImplementedError

    def get_order_detail(self, order: tblOrder):
        raise NotImplementedError

    def update_order_status(self, order: tblOrder):
        raise NotImplementedError

    def cancel_order(self, order: tblOrder):
        raise NotImplementedError

    def search_order(self, key: str, status: str | None, start: date, end: date):
        raise NotImplementedError
