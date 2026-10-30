"""Model package catalogue — Danh mục sản phẩm."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FitType(Enum):
    SLIM = "slim"
    REGULAR = "regular"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"


class Measure(Enum):
    CHEST = "chest"
    WAIST = "waist"
    HIP = "hip"
    LENGTH = "length"
    SLEEVE = "sleeve"
    INSEAM = "inseam"
    FOOT_LENGTH = "foot_length"


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"


class Season(Enum):
    SPRING_SUMMER = "spring_summer"
    AUTUMN_WINTER = "autumn_winter"
    ALL_SEASON = "all_season"


class StyleStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class VariantStatus(Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"


@dataclass(kw_only=True)
class Category:
    """Cây danh mục; `parentId` NULL = gốc.

    Relationships: Category (association, 0..*).
    """
    id: int | None = None
    name: str | None = None
    parentId: int | None = None


@dataclass(kw_only=True)
class Collection:
    """Bộ sưu tập theo mùa, năm."""
    id: int | None = None
    name: str | None = None
    season: Season | None = None
    year: int | None = None


@dataclass(kw_only=True)
class MaterialComponent:
    """Thành phần vải; `percent` 1–100, tổng của một style = 100 (kiểm ở ứng dụng)."""
    id: int | None = None
    material: str | None = None
    percent: int | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class ProductMedia:
    """Ảnh / video, thứ tự `sort_order`, có thể gắn màu."""
    id: int | None = None
    url: str | None = None
    media_type: MediaType | None = None
    colour: str | None = None
    sort_order: int | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class ProductVariant:
    """SKU = style + cỡ + màu, có giá (VND). UNIQUE `sku` và (`styleId`,`size_label`,`colour`).

    Relationships: RestockItem (aggregation, 1); StockLevel (aggregation, 1);
    StockMovement (aggregation, 0..*).
    """
    id: int | None = None
    sku: str | None = None
    size_label: str | None = None
    colour: str | None = None
    price: int | None = None
    status: VariantStatus | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class SizeChartEntry:
    """Một số đo của một cỡ; `value_cm > 0`."""
    id: int | None = None
    size_label: str | None = None
    measure: Measure | None = None
    value_cm: float | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class Style:
    """Mẫu sản phẩm. `code` UNIQUE. Hợp thành bởi biến thể, vật liệu, bảng cỡ, media.

    Relationships: Category (aggregation, 1); ProductMedia (composition, 0..*);
    Supplier (aggregation, 1); MaterialComponent (composition, 1..*);
    SizeChartEntry (composition, 0..*); Collection (aggregation, 0..1);
    ProductVariant (composition, 1..*).
    """
    id: int | None = None
    code: str | None = None
    name: str | None = None
    description: str | None = None
    brand: str | None = None
    fit_type: FitType | None = None
    care_instructions: str | None = None
    features: str | None = None
    model_info: str | None = None
    status: StyleStatus | None = None
    categoryId: int | None = None
    supplierId: int | None = None
    collectionId: int | None = None


def category_descendants(categories: list[Category], root_id: int) -> set[int]:
    """Id của `root_id` và mọi con cháu (dùng để chặn vòng lặp cây danh mục, lọc ở Frm)."""
    children: dict[int | None, list[int]] = {}
    for c in categories:
        children.setdefault(c.parentId, []).append(c.id)
    out, stack = set(), [root_id]
    while stack:
        cid = stack.pop()
        if cid in out:
            continue
        out.add(cid)
        stack.extend(children.get(cid, []))
    return out
