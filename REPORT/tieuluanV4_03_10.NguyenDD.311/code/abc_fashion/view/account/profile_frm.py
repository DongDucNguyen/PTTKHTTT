# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.profile_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.address_dao import AddressDAO
from abc_fashion.control.dao.customer_dao import CustomerDAO
from abc_fashion.control.dao.payment_method_dao import PaymentMethodDAO
from abc_fashion.control.dao.saved_size_dao import SavedSizeDAO
from abc_fashion.model.customer_data import tblAddress, tblPaymentMethod, tblSavedSize
from abc_fashion.model.user import tblCustomer


class ProfileFrm(tk.Toplevel):
    """ProfileFrm -- layer abc_fashion.view.account.
    Uses (control layer): CustomerDAO, AddressDAO, PaymentMethodDAO, SavedSizeDAO
    Opens (view layer): EditAddressFrm, LinkPaymentMethodFrm
    Holds (model layer): tblAddress, tblCustomer, tblPaymentMethod, tblSavedSize
    """

    customer: tblCustomer
    list_address: list[tblAddress]
    list_payment_method: list[tblPaymentMethod]
    list_saved_size: list[tblSavedSize]
    txt_full_name: ttk.Entry
    txt_phone: ttk.Entry
    txt_preferred_colours: ttk.Entry
    chk_marketing_consent: ttk.Checkbutton
    tbl_address: ttk.Treeview
    btn_add_address: ttk.Button
    btn_edit_address: ttk.Button
    btn_delete_address: ttk.Button
    tbl_payment_method: ttk.Treeview
    btn_link_payment_method: ttk.Button
    btn_remove_payment_method: ttk.Button
    tbl_saved_size: ttk.Treeview
    cbo_category: ttk.Combobox
    txt_size_label: ttk.Entry
    btn_save_size: ttk.Button
    btn_save: ttk.Button

    def __init__(self, customer: tblCustomer):
        super().__init__()
        self.customer = customer
        self.customer_dao = CustomerDAO()
        self.address_dao = AddressDAO()
        self.payment_method_dao = PaymentMethodDAO()
        self.saved_size_dao = SavedSizeDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_save(self):
        raise NotImplementedError

    def on_add_address(self):
        raise NotImplementedError

    def on_edit_address(self):
        raise NotImplementedError

    def on_delete_address(self):
        raise NotImplementedError

    def on_link_payment_method(self):
        raise NotImplementedError

    def on_remove_payment_method(self):
        raise NotImplementedError

    def on_save_size(self):
        raise NotImplementedError
