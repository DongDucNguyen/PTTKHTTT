# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order_admin.manage_order_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.dao.stock_movement_dao import StockMovementDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblStaffMember


class ManageOrderFrm(tk.Toplevel):
    """ManageOrderFrm -- layer abc_fashion.view.order_admin.
    Uses (control layer): OrderDAO, ShipmentDAO, PaymentDAO, StockMovementDAO, NotificationDAO, PaymentGateway, ShippingGateway, NotificationGateway
    Holds (model layer): tblOrder, tblStaffMember
    """

    staff: tblStaffMember
    order: tblOrder
    lbl_order_no: ttk.Label
    lbl_customer: ttk.Label
    lbl_status: ttk.Label
    tbl_order_item: ttk.Treeview
    tbl_payment: ttk.Treeview
    tbl_shipment: ttk.Treeview
    cbo_new_status: ttk.Combobox
    btn_update_status: ttk.Button
    txt_cancel_reason: ttk.Entry
    btn_cancel_order: ttk.Button
    btn_approve_cancel_request: ttk.Button
    btn_refund: ttk.Button

    def __init__(self, staff: tblStaffMember, order: tblOrder):
        super().__init__()
        self.staff = staff
        self.order = order
        self.order_dao = OrderDAO()
        self.shipment_dao = ShipmentDAO()
        self.payment_dao = PaymentDAO()
        self.stock_movement_dao = StockMovementDAO()
        self.notification_dao = NotificationDAO()
        self.payment_gateway = PaymentGateway()
        self.shipping_gateway = ShippingGateway()
        self.notification_gateway = NotificationGateway()
        raise NotImplementedError  # create and place the ttk widgets

    def on_update_status(self):
        raise NotImplementedError

    def on_cancel_order(self):
        raise NotImplementedError

    def on_approve_cancel_request(self):
        raise NotImplementedError

    def on_refund(self):
        raise NotImplementedError
