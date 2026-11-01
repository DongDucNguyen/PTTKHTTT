# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.stat) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from abc_fashion.model.catalogue import tblStyle
from abc_fashion.model.returns import ReturnReason


@dataclass(kw_only=True)
class ReturnStat(tblStyle):
    """ReturnStat -- layer abc_fashion.model.stat."""
    quantity_sold: int | None = None
    quantity_returned: int | None = None
    return_rate: float | None = None
    main_reason: ReturnReason | None = None


@dataclass(kw_only=True)
class StyleStat(tblStyle):
    """StyleStat -- layer abc_fashion.model.stat."""
    quantity_sold: int | None = None
    revenue: int | None = None
    order_count: int | None = None
