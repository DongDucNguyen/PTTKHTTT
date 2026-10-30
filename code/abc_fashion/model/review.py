"""Model package review — Đánh giá."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FitVote(Enum):
    RUNS_SMALL = "runs_small"
    TRUE_TO_SIZE = "true_to_size"
    RUNS_LARGE = "runs_large"


class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(kw_only=True)
class Review:
    """Đánh giá một dòng đơn (UNIQUE `orderItemId`); `rating` 1–5; `status` qua kiểm duyệt.

    Relationships: StaffMember (aggregation, 0..1).
    """
    id: int | None = None
    rating: int | None = None
    body: str | None = None
    size_purchased: str | None = None
    fit_vote: FitVote | None = None
    status: ReviewStatus | None = None
    moderation_note: str | None = None
    created_at: datetime | None = None
    orderItemId: int | None = None
    staffMemberId: int | None = None
