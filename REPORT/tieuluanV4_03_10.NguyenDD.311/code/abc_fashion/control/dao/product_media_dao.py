# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.product_media_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblProductMedia, tblStyle


class ProductMediaDAO(DAO):
    """ProductMediaDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblProductMedia
    """

    def get_media_by_style(self, style: tblStyle):
        raise NotImplementedError

    def add_media(self, media: tblProductMedia, style: tblStyle):
        raise NotImplementedError

    def delete_media(self, media: tblProductMedia):
        raise NotImplementedError
