"""Asset schemas."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


AssetType = Literal["stablecoin", "lst", "lrt", "pt", "native", "rwa"]


class AssetBase(BaseModel):
    """Base asset schema."""

    symbol: str = Field(..., max_length=20, examples=["USDC", "stETH"])
    name: str = Field(..., max_length=100, examples=["USD Coin", "Lido Staked ETH"])
    asset_type: Optional[AssetType] = Field(
        None,
        description="Asset type: stablecoin, lst, lrt, pt, native, rwa",
    )
    chain: str = Field(default="ethereum", max_length=20)
    contract_address: Optional[str] = Field(None, max_length=66)
    coingecko_id: Optional[str] = Field(None, max_length=100, examples=["usd-coin"])
    defillama_id: Optional[str] = Field(None, max_length=100)


class AssetCreate(AssetBase):
    """Schema for creating an asset."""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an asset."""

    symbol: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    asset_type: Optional[AssetType] = None
    chain: Optional[str] = Field(None, max_length=20)
    contract_address: Optional[str] = Field(None, max_length=66)
    coingecko_id: Optional[str] = Field(None, max_length=100)
    defillama_id: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class AssetResponse(AssetBase):
    """Schema for asset response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Optional computed fields
    current_price: Optional[float] = None
    price_change_24h: Optional[float] = None
    asset_rating: Optional[str] = None
    vault_eligibility: Optional[str] = None

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    """Schema for asset list response."""

    items: list[AssetResponse]
    total: int
    page: int
    size: int
