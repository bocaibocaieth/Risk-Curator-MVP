"""Monitor API endpoints."""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Asset
from app.exceptions import NotFoundError, ValidationError
from app.dependencies import get_price_service, get_tvl_service, get_monitor_service
from app.services.price_service import PriceService, TVLService
from app.services.monitor_service import MonitorService

router = APIRouter()


class PriceResponse(BaseModel):
    """Price response schema."""
    asset_id: int
    symbol: str
    price_usd: Optional[float] = None
    source: Optional[str] = None
    error: Optional[str] = None


class BatchPriceResponse(BaseModel):
    """Batch price response schema."""
    prices: List[PriceResponse]


class TVLResponse(BaseModel):
    """TVL response schema."""
    protocol: str
    tvl_usd: Optional[float] = None
    change_24h: Optional[float] = None
    error: Optional[str] = None


class MonitorCheckResponse(BaseModel):
    """Monitor check response schema."""
    checked_assets: int
    alerts_triggered: int
    messages: List[str]


@router.get("/prices/{asset_id}", response_model=PriceResponse)
async def get_asset_price(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    price_service: PriceService = Depends(get_price_service),
):
    """Get current price for a specific asset."""
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise NotFoundError("Asset", asset_id)

    price = await price_service.get_price(
        coingecko_id=asset.coingecko_id,
        chain=asset.chain,
        contract=asset.contract_address,
    )

    return PriceResponse(
        asset_id=asset.id,
        symbol=asset.symbol,
        price_usd=float(price) if price else None,
        source="coingecko" if asset.coingecko_id else "defillama",
        error=None if price else "Failed to fetch price",
    )


@router.get("/prices", response_model=BatchPriceResponse)
async def get_prices_batch(
    asset_ids: str = Query(..., description="Comma-separated asset IDs"),
    db: AsyncSession = Depends(get_db),
    price_service: PriceService = Depends(get_price_service),
):
    """Get prices for multiple assets."""
    try:
        ids = [int(id.strip()) for id in asset_ids.split(",")]
    except ValueError:
        raise ValidationError("Invalid asset IDs format", field="asset_ids")

    result = await db.execute(
        select(Asset).where(Asset.id.in_(ids))
    )
    assets = result.scalars().all()

    # Get prices for assets with coingecko_id
    coingecko_ids = [a.coingecko_id for a in assets if a.coingecko_id]
    batch_prices = {}
    if coingecko_ids:
        batch_prices = await price_service.get_prices_batch(coingecko_ids)

    prices = []
    for asset in assets:
        price = None
        if asset.coingecko_id and asset.coingecko_id in batch_prices:
            price = batch_prices[asset.coingecko_id]
        elif asset.contract_address:
            price = await price_service.get_price(
                chain=asset.chain,
                contract=asset.contract_address,
            )

        prices.append(
            PriceResponse(
                asset_id=asset.id,
                symbol=asset.symbol,
                price_usd=float(price) if price else None,
                source="coingecko" if asset.coingecko_id else "defillama",
                error=None if price else "Failed to fetch price",
            )
        )

    return BatchPriceResponse(prices=prices)


@router.get("/tvl/{protocol_slug}", response_model=TVLResponse)
async def get_protocol_tvl(
    protocol_slug: str,
    tvl_service: TVLService = Depends(get_tvl_service),
):
    """Get TVL for a protocol from DeFiLlama."""
    data = await tvl_service.get_protocol_tvl(protocol_slug)

    if data is None:
        return TVLResponse(
            protocol=protocol_slug,
            error="Failed to fetch TVL data",
        )

    # DeFiLlama returns TVL directly as a number
    tvl = data if isinstance(data, (int, float)) else None

    return TVLResponse(
        protocol=protocol_slug,
        tvl_usd=tvl,
    )


@router.post("/check", response_model=MonitorCheckResponse)
async def trigger_monitoring_check(
    db: AsyncSession = Depends(get_db),
    monitor: MonitorService = Depends(get_monitor_service),
):
    """Manually trigger a monitoring check cycle."""
    alerts = await monitor.run_monitoring_cycle()

    return MonitorCheckResponse(
        checked_assets=await db.scalar(
            select(func.count()).select_from(
                select(Asset).where(Asset.is_active == True).subquery()
            )
        ) or 0,
        alerts_triggered=len(alerts),
        messages=alerts,
    )
