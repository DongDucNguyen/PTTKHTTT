"""Model package assistant — Nhật ký trợ lý AI (Chương 3)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AssistantMode(Enum):
    MODEL = "model"
    BASIC = "basic"


class GroundingCheck(Enum):
    PRICE = "price"
    STOCK = "stock"
    FIT = "fit"
    FABRIC = "fabric"
    POPULARITY = "popularity"
    POLICY = "policy"
    HEALTH = "health"


@dataclass(kw_only=True)
class AssistantTurn:
    """Một lượt hỏi–đáp; `customerId` NULL với khách vãng lai. DAO gắn động `grounding_events`.

    Relationships: GroundingEvent (composition, 0..*); Customer (aggregation, 0..1);
    Style (aggregation, 0..1).
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
class GroundingEvent:
    """Câu bị loại khỏi câu trả lời vì không khớp dữ liệu (giá, tồn kho, …)."""
    id: int | None = None
    check_name: GroundingCheck | None = None
    removed_text: str | None = None
    assistantTurnId: int | None = None
