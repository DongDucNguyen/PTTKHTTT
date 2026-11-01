# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.order_item_dao) -- do not edit the signatures.
from __future__ import annotations

from datetime import date, datetime

from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblStyle


class OrderItemDAO(DAO):
    """OrderItemDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblOrderItem
    """

    def get_order_item_by_style(self, style: tblStyle, start: date, end: date):
        raise NotImplementedError
