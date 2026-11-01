# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.assistant) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class AssistantMode(Enum):
    """<<enumeration>> AssistantMode -- layer abc_fashion.model.assistant."""
    MODEL = "model"
    BASIC = "basic"


class GroundingCheck(Enum):
    """<<enumeration>> GroundingCheck -- layer abc_fashion.model.assistant."""
    PRICE = "price"
    STOCK = "stock"
    FIT = "fit"
    FABRIC = "fabric"
    POPULARITY = "popularity"
    POLICY = "policy"
    HEALTH = "health"


@dataclass(kw_only=True)
class tblAssistantTurn:
    """<<ORM Persistable>> tblAssistantTurn -- layer abc_fashion.model.assistant.
    Relationships: tblGroundingEvent (composition, 0..*); tblCustomer (aggregation, 0..1); tblStyle (aggregation, 0..1)
    """
    id: int | None = None
    question: str | None = None
    answer: str | None = None
    mode: AssistantMode | None = None
    model_name: str | None = None
    latency_ms: int | None = None
    created_at: datetime | None = None
    customerId: int | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class tblGroundingEvent:
    """<<ORM Persistable>> tblGroundingEvent -- layer abc_fashion.model.assistant."""
    id: int | None = None
    check_name: GroundingCheck | None = None
    removed_text: str | None = None
    assistantTurnId: int | None = None
