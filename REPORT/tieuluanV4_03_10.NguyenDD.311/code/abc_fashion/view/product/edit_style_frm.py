# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.product.edit_style_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.audit_log_entry_dao import AuditLogEntryDAO
from abc_fashion.control.dao.category_dao import CategoryDAO
from abc_fashion.control.dao.collection_dao import CollectionDAO
from abc_fashion.control.dao.material_component_dao import MaterialComponentDAO
from abc_fashion.control.dao.product_media_dao import ProductMediaDAO
from abc_fashion.control.dao.product_variant_dao import ProductVariantDAO
from abc_fashion.control.dao.size_chart_entry_dao import SizeChartEntryDAO
from abc_fashion.control.dao.style_dao import StyleDAO
from abc_fashion.control.dao.supplier_dao import SupplierDAO
from abc_fashion.model.catalogue import tblCategory, tblCollection, tblStyle
from abc_fashion.model.user import tblStaffMember, tblSupplier


class EditStyleFrm(tk.Toplevel):
    """EditStyleFrm -- layer abc_fashion.view.product.
    Uses (control layer): StyleDAO, CategoryDAO, CollectionDAO, SupplierDAO, ProductMediaDAO, MaterialComponentDAO, SizeChartEntryDAO, ProductVariantDAO, AuditLogEntryDAO
    Opens (view layer): EditVariantFrm
    Holds (model layer): tblCategory, tblCollection, tblStaffMember, tblStyle, tblSupplier
    """

    staff: tblStaffMember
    style: tblStyle
    list_category: list[tblCategory]
    list_supplier: list[tblSupplier]
    list_collection: list[tblCollection]
    txt_code: ttk.Entry
    txt_name: ttk.Entry
    txa_description: tk.Text
    txt_brand: ttk.Entry
    cbo_fit_type: ttk.Combobox
    txt_care_instructions: ttk.Entry
    txt_features: ttk.Entry
    txt_model_info: ttk.Entry
    cbo_status: ttk.Combobox
    cbo_category: ttk.Combobox
    cbo_supplier: ttk.Combobox
    cbo_collection: ttk.Combobox
    tbl_material: ttk.Treeview
    txt_material: ttk.Entry
    spn_percent: ttk.Spinbox
    btn_add_material: ttk.Button
    tbl_size_chart: ttk.Treeview
    txt_size_label: ttk.Entry
    cbo_measure: ttk.Combobox
    txt_value_cm: ttk.Entry
    btn_add_size_entry: ttk.Button
    tbl_media: ttk.Treeview
    btn_upload_media: ttk.Button
    tbl_variant: ttk.Treeview
    btn_add_variant: ttk.Button
    btn_edit_variant: ttk.Button
    btn_save: ttk.Button
    btn_reset: ttk.Button

    def __init__(self, staff: tblStaffMember, style: tblStyle | None):
        super().__init__()
        self.staff = staff
        self.style = style
        self.style_dao = StyleDAO()
        self.category_dao = CategoryDAO()
        self.collection_dao = CollectionDAO()
        self.supplier_dao = SupplierDAO()
        self.product_media_dao = ProductMediaDAO()
        self.material_component_dao = MaterialComponentDAO()
        self.size_chart_entry_dao = SizeChartEntryDAO()
        self.product_variant_dao = ProductVariantDAO()
        self.audit_log_entry_dao = AuditLogEntryDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_add_material(self):
        raise NotImplementedError

    def on_add_size_entry(self):
        raise NotImplementedError

    def on_upload_media(self):
        raise NotImplementedError

    def on_add_variant(self):
        raise NotImplementedError

    def on_edit_variant(self):
        raise NotImplementedError

    def on_save(self):
        raise NotImplementedError

    def on_reset(self):
        raise NotImplementedError
