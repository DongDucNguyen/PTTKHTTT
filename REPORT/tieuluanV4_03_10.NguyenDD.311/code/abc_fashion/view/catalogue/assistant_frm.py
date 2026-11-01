# Generated from the Visual Paradigm model "Design" (package abc_fashion.view.catalogue.assistant_frm) -- do not edit the signatures.
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.control.dao.assistant_turn_dao import AssistantTurnDAO
from abc_fashion.control.gateway.assistant_engine import AssistantEngine
from abc_fashion.model.assistant import tblAssistantTurn
from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.user import tblCustomer


class AssistantFrm(tk.Toplevel):
    """AssistantFrm -- layer abc_fashion.view.catalogue.
    Uses (control layer): AssistantTurnDAO, AssistantEngine
    Holds (model layer): tblAssistantTurn, tblCustomer, tblStyle
    """

    customer: tblCustomer | None
    style: tblStyle
    list_turn: list[tblAssistantTurn]
    txa_conversation: tk.Text
    txt_question: ttk.Entry
    btn_ask: ttk.Button
    lbl_mode: ttk.Label

    def __init__(self, customer: tblCustomer | None, style: tblStyle):
        super().__init__()
        self.customer = customer
        self.style = style
        self.assistant_turn_dao = AssistantTurnDAO()
        self.assistant_engine = AssistantEngine()
        raise NotImplementedError  # create and place the ttk widgets

    def on_ask(self):
        raise NotImplementedError
