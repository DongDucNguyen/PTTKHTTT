# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.stock_location_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO


class StockLocationDAO(DAO):
    """StockLocationDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblStockLocation
    """

    def get_all_stock_location(self):
        raise NotImplementedError
