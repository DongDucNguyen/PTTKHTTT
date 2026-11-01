# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.return_stat_dao) -- do not edit the signatures.
from __future__ import annotations

from datetime import date, datetime

from abc_fashion.control.dao.dao import DAO


class ReturnStatDAO(DAO):
    """ReturnStatDAO -- layer abc_fashion.control.dao.
    Holds (model layer): ReturnStat
    """

    def get_return_stat(self, start: date, end: date, reason: str | None):
        raise NotImplementedError
