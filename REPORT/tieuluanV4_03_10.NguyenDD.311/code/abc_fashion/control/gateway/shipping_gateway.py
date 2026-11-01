# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.gateway.shipping_gateway) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.model.fulfilment import tblShipment


class ShippingGateway:
    """ShippingGateway -- layer abc_fashion.control.gateway."""

    def create_shipment(self, shipment: tblShipment):
        raise NotImplementedError

    def get_tracking(self, shipment: tblShipment):
        raise NotImplementedError
