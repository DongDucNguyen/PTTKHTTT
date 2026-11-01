# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.review) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class FitVote(Enum):
    """<<enumeration>> FitVote -- layer abc_fashion.model.review."""
    RUNS_SMALL = "runs_small"
    TRUE_TO_SIZE = "true_to_size"
    RUNS_LARGE = "runs_large"


class ReviewStatus(Enum):
    """<<enumeration>> ReviewStatus -- layer abc_fashion.model.review."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(kw_only=True)
class tblReview:
    """<<ORM Persistable>> tblReview -- layer abc_fashion.model.review.
    Relationships: tblStaffMember (aggregation, 0..1)
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
