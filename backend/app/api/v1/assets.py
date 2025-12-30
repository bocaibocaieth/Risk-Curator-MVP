"""Asset API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Asset, AssetRating
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
)

router = APIRouter()


@router.get("", response_model=AssetListResponse)
async def list_assets(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = Query(None),
    chain: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all assets with optional filtering."""
    # Build query
    query = select(Asset).options(selectinload(Asset.rating))

    # Apply filters
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    if chain:
        query = query.where(Asset.chain == chain)
    if is_active is not None:
        query = query.where(Asset.is_active == is_active)
    if search:
        query = query.where(
            (Asset.symbol.ilike(f"%{search}%")) | (Asset.name.ilike(f"%{search}%"))
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(Asset.symbol)

    result = await db.execute(query)
    assets = result.scalars().all()

    # Build response with rating info
    items = []
    for asset in assets:
        response = AssetResponse.model_validate(asset)
        if asset.rating:
            response.asset_rating = asset.rating.asset_rating
            response.vault_eligibility = asset.rating.vault_eligibility
        items.append(response)

    return AssetListResponse(
        items=items,
        total=total or 0,
        page=page,
        size=size,
    )


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(
    data: AssetCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new asset."""
    # Check if asset with same symbol and chain exists
    existing = await db.execute(
        select(Asset).where(
            Asset.symbol == data.symbol,
            Asset.chain == data.chain,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Asset {data.symbol} on {data.chain} already exists",
        )

    asset = Asset(**data.model_dump())
    db.add(asset)
    await db.flush()
    await db.refresh(asset)

    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single asset by ID."""
    result = await db.execute(
        select(Asset)
        .options(selectinload(Asset.rating))
        .where(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    response = AssetResponse.model_validate(asset)
    if asset.rating:
        response.asset_rating = asset.rating.asset_rating
        response.vault_eligibility = asset.rating.vault_eligibility

    return response


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an asset."""
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)

    await db.flush()
    await db.refresh(asset)

    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an asset."""
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    await db.delete(asset)
