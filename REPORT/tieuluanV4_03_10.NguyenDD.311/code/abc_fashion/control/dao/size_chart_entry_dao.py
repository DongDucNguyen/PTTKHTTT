# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.size_chart_entry_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblSizeChartEntry, tblStyle


class SizeChartEntryDAO(DAO):
    """SizeChartEntryDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblSizeChartEntry
    """

    def get_size_chart_by_style(self, style: tblStyle):
        raise NotImplementedError

    def save_size_chart(self, style: tblStyle, entries: list[tblSizeChartEntry]):
        raise NotImplementedError
