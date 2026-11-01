# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.product.edit_variant_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.stock_location_dao import StockLocationDAO
from abc_fashion.model.catalogue import tblProductVariant, tblStyle
from abc_fashion.model.inventory import tblStockLocation
from abc_fashion.model.user import tblStaffMember


class EditVariantFrm(tk.Toplevel):
    """EditVariantFrm -- layer abc_fashion.view.product.
    Uses (control layer): ProductVariantDAO, StockLocationDAO, StockLevelDAO
    Holds (model layer): tblProductVariant, tblStaffMember, tblStockLocation, tblStyle
    """

    staff: tblStaffMember
    style: tblStyle
    variant: tblProductVariant | None
    list_stock_location: list[tblStockLocation]
    txt_sku: ttk.Entry
    txt_size_label: ttk.Entry
    txt_colour: ttk.Entry
    txt_price: ttk.Entry
    cbo_status: ttk.Combobox
    cbo_stock_location: ttk.Combobox
    spn_reorder_point: ttk.Spinbox
    btn_save: ttk.Button
    btn_reset: ttk.Button

    def __init__(self, staff: tblStaffMember, style: tblStyle, variant: tblProductVariant | None):
        super().__init__()
        self.staff = staff
        self.style = style
        self.variant = variant
        self.product_variant_dao = ProductVariantDAO()
        self.stock_location_dao = StockLocationDAO()
        self.stock_level_dao = StockLevelDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_save(self):
        raise NotImplementedError

    def on_reset(self):
        raise NotImplementedError
