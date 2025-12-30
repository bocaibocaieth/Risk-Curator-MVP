"""Pydantic schemas."""

from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
)
from app.schemas.rating import (
    IssuerRiskInput,
    CreditRiskInput,
    OperationalRiskInput,
    AssetRatingCreate,
    AssetRatingUpdate,
    AssetRatingResponse,
)
from app.schemas.alert import (
    AlertConfigCreate,
    AlertConfigUpdate,
    AlertConfigResponse,
    AlertHistoryResponse,
)

__all__ = [
    # Asset
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AssetListResponse",
    # Rating
    "IssuerRiskInput",
    "CreditRiskInput",
    "OperationalRiskInput",
    "AssetRatingCreate",
    "AssetRatingUpdate",
    "AssetRatingResponse",
    # Alert
    "AlertConfigCreate",
    "AlertConfigUpdate",
    "AlertConfigResponse",
    "AlertHistoryResponse",
]
