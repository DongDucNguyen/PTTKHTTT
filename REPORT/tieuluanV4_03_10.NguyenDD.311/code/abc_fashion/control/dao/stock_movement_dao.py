# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.stock_movement_dao) -- do not edit the signatures.
from __future__ import annotations

from datetime import date, datetime

from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblProductVariant
from abc_fashion.model.inventory import tblStockMovement


class StockMovementDAO(DAO):
    """StockMovementDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblStockMovement
    """

    def add_stock_movement(self, movement: tblStockMovement):
        raise NotImplementedError

    def get_movement_by_variant(self, variant: tblProductVariant, start: date, end: date, reason: str | None):
        raise NotImplementedError
