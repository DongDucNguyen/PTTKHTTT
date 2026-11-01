# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.checkout.checkout_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.address_dao import AddressDAO
from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.payment_method_dao import PaymentMethodDAO
from abc_fashion.control.dao.voucher_dao import VoucherDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.model.customer_data import tblAddress, tblPaymentMethod
from abc_fashion.model.sales import tblCart, tblOrder, tblVoucher
from abc_fashion.model.user import tblCustomer


class CheckoutFrm(tk.Toplevel):
    """CheckoutFrm -- layer abc_fashion.view.checkout.
    Uses (control layer): AddressDAO, PaymentMethodDAO, VoucherDAO, OrderDAO, PaymentDAO, NotificationDAO, PaymentGateway, NotificationGateway
    Opens (view layer): ConfirmOrderFrm
    Holds (model layer): tblAddress, tblCart, tblCustomer, tblOrder, tblPaymentMethod, tblVoucher
    """

    customer: tblCustomer
    cart: tblCart
    order: tblOrder
    list_address: list[tblAddress]
    list_payment_method: list[tblPaymentMethod]
    list_voucher: list[tblVoucher]
    tbl_order_item: ttk.Treeview
    cbo_address: ttk.Combobox
    btn_add_address: ttk.Button
    rdo_delivery_service: ttk.Radiobutton
    txt_voucher_code: ttk.Entry
    btn_apply_voucher: ttk.Button
    rdo_payment_method: ttk.Radiobutton
    cbo_linked_method: ttk.Combobox
    txt_note: ttk.Entry
    lbl_subtotal: ttk.Label
    lbl_discount: ttk.Label
    lbl_shipping_fee: ttk.Label
    lbl_grand_total: ttk.Label
    btn_place_order: ttk.Button
    btn_back: ttk.Button

    def __init__(self, customer: tblCustomer, cart: tblCart):
        super().__init__()
        self.customer = customer
        self.cart = cart
        self.address_dao = AddressDAO()
        self.payment_method_dao = PaymentMethodDAO()
        self.voucher_dao = VoucherDAO()
        self.order_dao = OrderDAO()
        self.payment_dao = PaymentDAO()
        self.notification_dao = NotificationDAO()
        self.payment_gateway = PaymentGateway()
        self.notification_gateway = NotificationGateway()
        raise NotImplementedError  # create and place the ttk widgets

    def on_add_address(self):
        raise NotImplementedError

    def on_change_delivery_service(self):
        raise NotImplementedError

    def on_apply_voucher(self):
        raise NotImplementedError

    def on_place_order(self):
        raise NotImplementedError

    def on_back(self):
        raise NotImplementedError
