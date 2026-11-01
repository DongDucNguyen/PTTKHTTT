# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.returns.process_return_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.notification_dao import NotificationDAO
from abc_fashion.control.dao.payment_dao import PaymentDAO
from abc_fashion.control.dao.return_request_dao import ReturnRequestDAO
from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.gateway.notification_gateway import NotificationGateway
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.model.returns import tblReturnRequest
from abc_fashion.model.user import tblStaffMember


class ProcessReturnFrm(tk.Toplevel):
    """ProcessReturnFrm -- layer abc_fashion.view.returns.
    Uses (control layer): ReturnRequestDAO, ShipmentDAO, PaymentDAO, NotificationDAO, PaymentGateway, ShippingGateway, NotificationGateway
    Holds (model layer): tblReturnRequest, tblStaffMember
    """

    staff: tblStaffMember
    return_request: tblReturnRequest
    lbl_return_no: ttk.Label
    lbl_order_no: ttk.Label
    lbl_customer: ttk.Label
    lbl_return_type: ttk.Label
    lbl_reason: ttk.Label
    lbl_status: ttk.Label
    tbl_return_item: ttk.Treeview
    cnv_evidence: tk.Canvas
    txa_decision_note: tk.Text
    btn_authorise: ttk.Button
    btn_reject: ttk.Button
    btn_create_pickup: ttk.Button
    btn_refund: ttk.Button
    btn_ship_replacement: ttk.Button
    btn_close: ttk.Button

    def __init__(self, staff: tblStaffMember, return_request: tblReturnRequest):
        super().__init__()
        self.staff = staff
        self.return_request = return_request
        self.return_request_dao = ReturnRequestDAO()
        self.shipment_dao = ShipmentDAO()
        self.payment_dao = PaymentDAO()
        self.notification_dao = NotificationDAO()
        self.payment_gateway = PaymentGateway()
        self.shipping_gateway = ShippingGateway()
        self.notification_gateway = NotificationGateway()
        raise NotImplementedError  # create and place the ttk widgets

    def on_authorise(self):
        raise NotImplementedError

    def on_reject(self):
        raise NotImplementedError

    def on_create_pickup(self):
        raise NotImplementedError

    def on_refund(self):
        raise NotImplementedError

    def on_ship_replacement(self):
        raise NotImplementedError

    def on_close(self):
        raise NotImplementedError
