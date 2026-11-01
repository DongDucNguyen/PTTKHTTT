# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.notification_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.customer_data import tblNotification
from abc_fashion.model.user import tblCustomer


class NotificationDAO(DAO):
    """NotificationDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblNotification
    """

    def add_notification(self, notification: tblNotification, customer: tblCustomer):
        raise NotImplementedError
