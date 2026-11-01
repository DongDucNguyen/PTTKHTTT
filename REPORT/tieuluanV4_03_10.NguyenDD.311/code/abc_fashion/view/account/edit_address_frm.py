# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.account.edit_address_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.address_dao import AddressDAO
from abc_fashion.model.customer_data import tblAddress
from abc_fashion.model.user import tblCustomer


class EditAddressFrm(tk.Toplevel):
    """EditAddressFrm -- layer abc_fashion.view.account.
    Uses (control layer): AddressDAO
    Holds (model layer): tblAddress, tblCustomer
    """

    customer: tblCustomer
    address: tblAddress | None
    txt_recipient_name: ttk.Entry
    txt_phone: ttk.Entry
    txt_street: ttk.Entry
    txt_ward: ttk.Entry
    txt_district: ttk.Entry
    chk_is_default: ttk.Checkbutton
    btn_save: ttk.Button
    btn_reset: ttk.Button

    def __init__(self, customer: tblCustomer, address: tblAddress | None):
        super().__init__()
        self.customer = customer
        self.address = address
        self.address_dao = AddressDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_save(self):
        raise NotImplementedError

    def on_reset(self):
        raise NotImplementedError
