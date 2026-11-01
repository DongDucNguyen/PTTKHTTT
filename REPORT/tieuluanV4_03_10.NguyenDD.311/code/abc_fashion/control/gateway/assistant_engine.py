# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.gateway.assistant_engine) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.review import tblReview


class AssistantEngine:
    """AssistantEngine -- layer abc_fashion.control.gateway."""

    def ask(self, question: str, style: tblStyle):
        raise NotImplementedError

    def summarise_reviews(self, style: tblStyle):
        raise NotImplementedError

    def moderate(self, review: tblReview):
        raise NotImplementedError
