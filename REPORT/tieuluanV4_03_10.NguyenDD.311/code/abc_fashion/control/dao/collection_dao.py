# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.collection_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO


class CollectionDAO(DAO):
    """CollectionDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblCollection
    """

    def get_all_collection(self):
        raise NotImplementedError
