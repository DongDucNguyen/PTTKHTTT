# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.catalogue.style_detail_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.cart_dao import CartDAO
from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.control.dao.promotion_dao import PromotionDAO
from abc_fashion.control.dao.review_dao import ReviewDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.control.gateway.assistant_engine import AssistantEngine
from abc_fashion.model.catalogue import tblProductMedia, tblProductVariant, tblStyle
from abc_fashion.model.review import tblReview
from abc_fashion.model.user import tblCustomer


class StyleDetailFrm(tk.Toplevel):
    """StyleDetailFrm -- layer abc_fashion.view.catalogue.
    Uses (control layer): StyleDAO, ProductVariantDAO, ReviewDAO, StockLevelDAO, PromotionDAO, CartDAO, AssistantEngine
    Opens (view layer): AssistantFrm
    Holds (model layer): tblCustomer, tblProductMedia, tblProductVariant, tblReview, tblStyle
    """

    customer: tblCustomer | None
    style: tblStyle
    list_variant: list[tblProductVariant]
    list_media: list[tblProductMedia]
    list_review: list[tblReview]
    selected_variant: tblProductVariant | None
    lbl_name: ttk.Label
    lbl_brand: ttk.Label
    lbl_price: ttk.Label
    lbl_promotion: ttk.Label
    cnv_media: tk.Canvas
    txa_description: tk.Text
    lbl_material: ttk.Label
    lbl_care_instructions: ttk.Label
    lbl_model_info: ttk.Label
    tbl_size_chart: ttk.Treeview
    cbo_colour: ttk.Combobox
    cbo_size: ttk.Combobox
    lbl_availability: ttk.Label
    spn_quantity: ttk.Spinbox
    btn_add_to_cart: ttk.Button
    lbl_review_summary: ttk.Label
    tbl_review: ttk.Treeview
    btn_ask_assistant: ttk.Button

    def __init__(self, customer: tblCustomer | None, style: tblStyle):
        super().__init__()
        self.customer = customer
        self.style = style
        self.style_dao = StyleDAO()
        self.product_variant_dao = ProductVariantDAO()
        self.review_dao = ReviewDAO()
        self.stock_level_dao = StockLevelDAO()
        self.promotion_dao = PromotionDAO()
        self.cart_dao = CartDAO()
        self.assistant_engine = AssistantEngine()
        raise NotImplementedError  # create and place the ttk widgets

    def on_select_variant(self):
        raise NotImplementedError

    def on_add_to_cart(self):
        raise NotImplementedError

    def on_ask_assistant(self):
        raise NotImplementedError
