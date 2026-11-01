# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.style_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblCategory, tblStyle


class StyleDAO(DAO):
    """StyleDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblStyle
    """

    def search_style(self, key: str):
        raise NotImplementedError

    def search_style_by_ids(self, ids: list[int]):
        raise NotImplementedError

    def get_style_by_category(self, category: tblCategory, size: str, colour: str, fit_type: str, min_price: int, max_price: int, sort: str):
        raise NotImplementedError

    def get_style_detail(self, style: tblStyle):
        raise NotImplementedError

    def add_style(self, style: tblStyle):
        raise NotImplementedError

    def update_style(self, style: tblStyle):
        raise NotImplementedError

    def deactivate_style(self, style: tblStyle):
        raise NotImplementedError
