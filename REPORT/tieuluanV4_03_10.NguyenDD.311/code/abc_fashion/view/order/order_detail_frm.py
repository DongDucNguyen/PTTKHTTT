# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order.order_detail_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.order_dao import OrderDAO
from abc_fashion.model.sales import tblOrder
from abc_fashion.model.user import tblCustomer


class OrderDetailFrm(tk.Toplevel):
    """OrderDetailFrm -- layer abc_fashion.view.order.
    Uses (control layer): OrderDAO
    Opens (view layer): TrackShipmentFrm, CancelRequestFrm, ReviewFrm, ReturnRequestFrm
    Holds (model layer): tblCustomer, tblOrder
    """

    customer: tblCustomer
    order: tblOrder
    lbl_order_no: ttk.Label
    lbl_placed_at: ttk.Label
    lbl_status: ttk.Label
    lbl_address: ttk.Label
    tbl_order_item: ttk.Treeview
    tbl_payment: ttk.Treeview
    tbl_shipment: ttk.Treeview
    lbl_subtotal: ttk.Label
    lbl_discount: ttk.Label
    lbl_shipping_fee: ttk.Label
    lbl_grand_total: ttk.Label
    btn_track: ttk.Button
    btn_cancel_request: ttk.Button
    btn_confirm_received: ttk.Button
    btn_review: ttk.Button
    btn_return: ttk.Button

    def __init__(self, customer: tblCustomer, order: tblOrder):
        super().__init__()
        self.customer = customer
        self.order = order
        self.order_dao = OrderDAO()
        raise NotImplementedError  # create and place the ttk widgets

    def on_track(self):
        raise NotImplementedError

    def on_cancel_request(self):
        raise NotImplementedError

    def on_confirm_received(self):
        raise NotImplementedError

    def on_review(self):
        raise NotImplementedError

    def on_return(self):
        raise NotImplementedError
