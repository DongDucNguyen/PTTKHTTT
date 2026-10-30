"""Model package stat — Lớp thống kê cho báo cáo (không có bảng)."""
from __future__ import annotations

from dataclasses import dataclass

from abc_fashion.model.catalogue import Style
from abc_fashion.model.returns import ReturnReason


@dataclass(kw_only=True)
class ReturnStat(Style):
    """Một style + số liệu trả; do `ReturnStatDAO` tính."""
    quantity_sold: int | None = None
    quantity_returned: int | None = None
    return_rate: float | None = None
    main_reason: ReturnReason | None = None


@dataclass(kw_only=True)
class StyleStat(Style):
    """Một style + số liệu bán; do `StyleStatDAO` tính."""
    quantity_sold: int | None = None
    revenue: int | None = None
    order_count: int | None = None
