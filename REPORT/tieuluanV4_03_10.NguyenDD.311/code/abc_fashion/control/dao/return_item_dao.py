# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.return_item_dao) -- do not edit the signatures.
from __future__ import annotations

from datetime import date, datetime

from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblStyle


class ReturnItemDAO(DAO):
    """ReturnItemDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblReturnItem
    """

    def get_return_item_by_style(self, style: tblStyle, start: date, end: date):
        raise NotImplementedError
