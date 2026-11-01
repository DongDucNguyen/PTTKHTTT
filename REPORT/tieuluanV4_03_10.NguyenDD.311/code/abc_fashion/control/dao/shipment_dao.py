# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.shipment_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.fulfilment import tblShipment, tblShipmentEvent
from abc_fashion.model.sales import tblOrder


class ShipmentDAO(DAO):
    """ShipmentDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblShipment
    """

    def get_shipment_by_order(self, order: tblOrder):
        raise NotImplementedError

    def get_shipment_event(self, shipment: tblShipment):
        raise NotImplementedError

    def update_shipment(self, shipment: tblShipment):
        raise NotImplementedError

    def add_shipment_event(self, event: tblShipmentEvent, shipment: tblShipment):
        raise NotImplementedError

    def add_shipment(self, shipment: tblShipment, order: tblOrder):
        raise NotImplementedError
