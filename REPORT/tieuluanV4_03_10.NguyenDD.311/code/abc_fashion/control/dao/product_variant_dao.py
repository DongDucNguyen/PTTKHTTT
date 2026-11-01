# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.product_variant_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblProductVariant, tblStyle


class ProductVariantDAO(DAO):
    """ProductVariantDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblProductVariant
    """

    def get_variant_by_style(self, style: tblStyle):
        raise NotImplementedError

    def search_variant(self, key: str):
        raise NotImplementedError

    def add_variant(self, variant: tblProductVariant, style: tblStyle):
        raise NotImplementedError

    def update_variant(self, variant: tblProductVariant):
        raise NotImplementedError
