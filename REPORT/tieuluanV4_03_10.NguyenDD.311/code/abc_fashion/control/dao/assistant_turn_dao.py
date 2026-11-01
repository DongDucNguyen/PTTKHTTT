# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.assistant_turn_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.assistant import tblAssistantTurn
from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.user import tblCustomer


class AssistantTurnDAO(DAO):
    """AssistantTurnDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblAssistantTurn
    """

    def add_assistant_turn(self, turn: tblAssistantTurn, customer: tblCustomer | None, style: tblStyle):
        raise NotImplementedError

    def get_turn_by_customer(self, customer: tblCustomer, style: tblStyle):
        raise NotImplementedError
