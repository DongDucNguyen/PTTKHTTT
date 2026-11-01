# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.promotion.edit_promotion_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.promotion_dao import PromotionDAO
from abc_fashion.control.dao.voucher_dao import VoucherDAO
from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.sales import tblPromotion, tblVoucher
from abc_fashion.model.user import tblStaffMember


class EditPromotionFrm(tk.Toplevel):
    """EditPromotionFrm -- layer abc_fashion.view.promotion.
    Uses (control layer): PromotionDAO, VoucherDAO
    Opens (view layer): SelectStyleFrm
    Holds (model layer): tblPromotion, tblStaffMember, tblStyle, tblVoucher
    """

    staff: tblStaffMember
    promotion: tblPromotion
    list_style: list[tblStyle]
    list_voucher: list[tblVoucher]
    txt_name: ttk.Entry
    cbo_promo_type: ttk.Combobox
    cbo_discount_type: ttk.Combobox
    txt_discount_value: ttk.Entry
    txt_min_order_value: ttk.Entry
    dte_starts_at: DateEntry
    dte_ends_at: DateEntry
    cbo_status: ttk.Combobox
    tbl_style: ttk.Treeview
    btn_add_style: ttk.Button
    btn_remove_style: ttk.Button
    tbl_voucher: ttk.Treeview
    txt_voucher_code: ttk.Entry
    spn_usage_limit: ttk.Spinbox
    btn_add_voucher: ttk.Button
    btn_save: ttk.Button
    btn_reset: ttk.Button

    def __init__(self, staff: tblStaffMember, promotion: tblPromotion | None):
        super().__init__()
        self.staff = staff
        self.promotion = promotion
        self.promotion_dao = PromotionDAO()
        self.voucher_dao = VoucherDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_add_style(self):
        raise NotImplementedError

    def on_remove_style(self):
        raise NotImplementedError

    def on_add_voucher(self):
        raise NotImplementedError

    def on_save(self):
        raise NotImplementedError

    def on_reset(self):
        raise NotImplementedError
