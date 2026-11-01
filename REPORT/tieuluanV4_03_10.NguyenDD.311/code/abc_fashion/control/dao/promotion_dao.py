# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.promotion_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.sales import tblPromotion


class PromotionDAO(DAO):
    """PromotionDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblPromotion
    """

    def get_active_promotion_by_style(self, style: tblStyle):
        raise NotImplementedError

    def search_promotion(self, key: str, status: str | None):
        raise NotImplementedError

    def get_promotion_detail(self, promotion: tblPromotion):
        raise NotImplementedError

    def add_promotion(self, promotion: tblPromotion):
        raise NotImplementedError

    def update_promotion(self, promotion: tblPromotion):
        raise NotImplementedError
