# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.order.track_shipment_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.shipment_dao import ShipmentDAO
from abc_fashion.control.gateway.shipping_gateway import ShippingGateway
from abc_fashion.model.fulfilment import tblShipment


class TrackShipmentFrm(tk.Toplevel):
    """TrackShipmentFrm -- layer abc_fashion.view.order.
    Uses (control layer): ShipmentDAO, ShippingGateway
    Holds (model layer): tblShipment
    """

    shipment: tblShipment
    lbl_carrier: ttk.Label
    lbl_tracking_no: ttk.Label
    lbl_status: ttk.Label
    tbl_shipment_record: ttk.Treeview
    tbl_shipment_event: ttk.Treeview
    btn_refresh: ttk.Button

    def __init__(self, shipment: tblShipment):
        super().__init__()
        self.shipment = shipment
        self.shipment_dao = ShipmentDAO()
        self.shipping_gateway = ShippingGateway()
        raise NotImplementedError  # create and place the ttk widgets

    def on_refresh(self):
        raise NotImplementedError
