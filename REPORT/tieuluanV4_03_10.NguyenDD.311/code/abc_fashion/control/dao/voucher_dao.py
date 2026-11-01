# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.voucher_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.sales import tblPromotion, tblVoucher


class VoucherDAO(DAO):
    """VoucherDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblVoucher
    """

    def get_voucher_by_code(self, code: str):
        raise NotImplementedError

    def add_voucher(self, voucher: tblVoucher, promotion: tblPromotion):
        raise NotImplementedError

    def get_voucher_by_promotion(self, promotion: tblPromotion):
        raise NotImplementedError
