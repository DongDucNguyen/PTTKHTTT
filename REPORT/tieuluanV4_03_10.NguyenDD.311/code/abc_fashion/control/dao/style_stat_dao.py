# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.style_stat_dao) -- do not edit the signatures.
from __future__ import annotations

from datetime import date, datetime

from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblCategory, tblCollection


class StyleStatDAO(DAO):
    """StyleStatDAO -- layer abc_fashion.control.dao.
    Holds (model layer): StyleStat
    """

    def get_style_stat(self, start: date, end: date, category: tblCategory | None, collection: tblCollection | None):
        raise NotImplementedError
