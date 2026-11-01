# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.gateway.notification_gateway) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.model.customer_data import tblNotification


class NotificationGateway:
    """NotificationGateway -- layer abc_fashion.control.gateway."""

    def send(self, notification: tblNotification):
        raise NotImplementedError
