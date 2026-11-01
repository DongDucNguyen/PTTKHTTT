# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.category_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblCategory


class CategoryDAO(DAO):
    """CategoryDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblCategory
    """

    def get_all_category(self):
        raise NotImplementedError

    def add_category(self, category: tblCategory):
        raise NotImplementedError

    def update_category(self, category: tblCategory):
        raise NotImplementedError
