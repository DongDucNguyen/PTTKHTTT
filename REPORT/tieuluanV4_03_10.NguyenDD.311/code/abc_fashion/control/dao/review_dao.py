# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.review_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.review import tblReview
from abc_fashion.model.sales import tblOrderItem
from abc_fashion.model.user import tblStaffMember


class ReviewDAO(DAO):
    """ReviewDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblReview
    """

    def get_approved_review_by_style(self, style: tblStyle):
        raise NotImplementedError

    def add_review(self, review: tblReview, order_item: tblOrderItem):
        raise NotImplementedError

    def is_reviewed(self, order_item: tblOrderItem):
        raise NotImplementedError

    def search_review(self, key: str, status: str | None, rating: int | None):
        raise NotImplementedError

    def update_review(self, review: tblReview, staff: tblStaffMember):
        raise NotImplementedError
