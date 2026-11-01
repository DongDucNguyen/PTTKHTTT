# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.stock_level_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblProductVariant
from abc_fashion.model.inventory import tblStockLevel, tblStockLocation, tblStockMovement
from abc_fashion.model.sales import tblCartItem, tblOrder


class StockLevelDAO(DAO):
    """StockLevelDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblStockLevel
    """

    def get_stock_level_by_variant(self, variant: tblProductVariant):
        raise NotImplementedError

    def check_availability(self, items: list[tblCartItem]):
        raise NotImplementedError

    def reserve_stock(self, order: tblOrder):
        raise NotImplementedError

    def add_stock_level(self, level: tblStockLevel, variant: tblProductVariant, location: tblStockLocation):
        raise NotImplementedError

    def search_stock_level(self, location: tblStockLocation | None, key: str, below_reorder_point: bool):
        raise NotImplementedError

    def adjust_stock(self, level: tblStockLevel, movement: tblStockMovement):
        raise NotImplementedError
