# Generated from the Visual Paradigm model "Design" (package abc_fashion.model.catalogue) -- do not edit the signatures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class FitType(Enum):
    """<<enumeration>> FitType -- layer abc_fashion.model.catalogue."""
    SLIM = "slim"
    REGULAR = "regular"
    RELAXED = "relaxed"
    OVERSIZED = "oversized"


class Measure(Enum):
    """<<enumeration>> Measure -- layer abc_fashion.model.catalogue."""
    CHEST = "chest"
    WAIST = "waist"
    HIP = "hip"
    LENGTH = "length"
    SLEEVE = "sleeve"
    INSEAM = "inseam"
    FOOT_LENGTH = "foot_length"


class MediaType(Enum):
    """<<enumeration>> MediaType -- layer abc_fashion.model.catalogue."""
    IMAGE = "image"
    VIDEO = "video"


class Season(Enum):
    """<<enumeration>> Season -- layer abc_fashion.model.catalogue."""
    SPRING_SUMMER = "spring_summer"
    AUTUMN_WINTER = "autumn_winter"
    ALL_SEASON = "all_season"


class StyleStatus(Enum):
    """<<enumeration>> StyleStatus -- layer abc_fashion.model.catalogue."""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class VariantStatus(Enum):
    """<<enumeration>> VariantStatus -- layer abc_fashion.model.catalogue."""
    ACTIVE = "active"
    DISCONTINUED = "discontinued"


@dataclass(kw_only=True)
class tblCategory:
    """<<ORM Persistable>> tblCategory -- layer abc_fashion.model.catalogue.
    Relationships: tblCategory (association, 0..*)
    """
    id: int | None = None
    name: str | None = None
    parentId: int | None = None


@dataclass(kw_only=True)
class tblCollection:
    """<<ORM Persistable>> tblCollection -- layer abc_fashion.model.catalogue."""
    id: int | None = None
    name: str | None = None
    season: Season | None = None
    year: int | None = None


@dataclass(kw_only=True)
class tblMaterialComponent:
    """<<ORM Persistable>> tblMaterialComponent -- layer abc_fashion.model.catalogue."""
    id: int | None = None
    material: str | None = None
    percent: int | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class tblProductMedia:
    """<<ORM Persistable>> tblProductMedia -- layer abc_fashion.model.catalogue."""
    id: int | None = None
    url: str | None = None
    media_type: MediaType | None = None
    colour: str | None = None
    sort_order: int | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class tblProductVariant:
    """<<ORM Persistable>> tblProductVariant -- layer abc_fashion.model.catalogue.
    Relationships: tblRestockItem (aggregation, 1); tblStockLevel (aggregation, 1); tblStockMovement (aggregation, 0..*)
    """
    id: int | None = None
    sku: str | None = None
    size_label: str | None = None
    colour: str | None = None
    price: int | None = None
    status: VariantStatus | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class tblSizeChartEntry:
    """<<ORM Persistable>> tblSizeChartEntry -- layer abc_fashion.model.catalogue."""
    id: int | None = None
    size_label: str | None = None
    measure: Measure | None = None
    value_cm: float | None = None
    styleId: int | None = None


@dataclass(kw_only=True)
class tblStyle:
    """<<ORM Persistable>> tblStyle -- layer abc_fashion.model.catalogue.
    Relationships: tblCategory (aggregation, 1); tblProductMedia (composition, 0..*); tblSupplier (aggregation, 1); tblMaterialComponent (composition, 1..*); tblSizeChartEntry (composition, 0..*); tblCollection (aggregation, 0..1); tblProductVariant (composition, 1..*)
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
