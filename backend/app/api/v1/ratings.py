"""Rating API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Asset, AssetRating
from app.schemas.rating import (
    AssetRatingCreate,
    AssetRatingUpdate,
    AssetRatingResponse,
    RatingListResponse,
)
from app.services.rating_calculator import RatingCalculator

router = APIRouter()
calculator = RatingCalculator()


@router.get("/assets", response_model=RatingListResponse)
async def list_asset_ratings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    asset_rating: Optional[str] = Query(None, description="Filter by rating grade"),
    vault_eligibility: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all asset ratings with optional filtering."""
    query = select(AssetRating).options(selectinload(AssetRating.asset))

    # Apply filters
    if asset_rating:
        query = query.where(AssetRating.asset_rating == asset_rating.upper())
    if vault_eligibility:
        query = query.where(AssetRating.vault_eligibility == vault_eligibility)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(AssetRating.rated_at.desc())

    result = await db.execute(query)
    ratings = result.scalars().all()

    # Build response with asset info
    items = []
    for rating in ratings:
        response = AssetRatingResponse.model_validate(rating)
        if rating.asset:
            response.asset_symbol = rating.asset.symbol
            response.asset_name = rating.asset.name
        items.append(response)

    return RatingListResponse(
        items=items,
        total=total or 0,
        page=page,
        size=size,
    )


@router.post("/assets", response_model=AssetRatingResponse, status_code=201)
async def create_asset_rating(
    data: AssetRatingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new asset rating."""
    # Check if asset exists
    result = await db.execute(
        select(Asset).where(Asset.id == data.asset_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Check if rating already exists
    existing = await db.execute(
        select(AssetRating).where(AssetRating.asset_id == data.asset_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Rating already exists for this asset. Use PUT to update.",
        )

    # Compute ratings
    computed = calculator.compute_full_asset_rating(
        issuer_social=data.issuer.social_score,
        issuer_decentralization=data.issuer.decentralization_score,
        issuer_technical=data.issuer.technical_score,
        credit_risk=data.credit.credit_risk_score,
        operational_lindy=data.operational.lindy_score,
        operational_audit=data.operational.audit_score,
        operational_transparency=data.operational.transparency_score,
    )

    # Create rating record
    rating = AssetRating(
        asset_id=data.asset_id,
        # Issuer scores
        issuer_social_score=data.issuer.social_score,
        issuer_decentralization_score=data.issuer.decentralization_score,
        issuer_technical_score=data.issuer.technical_score,
        # Credit score
        credit_risk_score=data.credit.credit_risk_score,
        # Operational scores
        operational_lindy_score=data.operational.lindy_score,
        operational_audit_score=data.operational.audit_score,
        operational_transparency_score=data.operational.transparency_score,
        # Computed ratings
        issuer_risk_rating=computed["issuer_risk_rating"],
        operational_risk_rating=computed["operational_risk_rating"],
        asset_rating=computed["asset_rating"],
        vault_eligibility=computed["vault_eligibility"],
        # Metadata
        rated_by=data.rated_by,
        rating_notes=data.rating_notes,
    )

    db.add(rating)
    await db.flush()
    await db.refresh(rating)

    response = AssetRatingResponse.model_validate(rating)
    response.asset_symbol = asset.symbol
    response.asset_name = asset.name

    return response


@router.get("/assets/{asset_id}", response_model=AssetRatingResponse)
async def get_asset_rating(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get rating for a specific asset."""
    result = await db.execute(
        select(AssetRating)
        .options(selectinload(AssetRating.asset))
        .where(AssetRating.asset_id == asset_id)
    )
    rating = result.scalar_one_or_none()

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found for this asset")

    response = AssetRatingResponse.model_validate(rating)
    if rating.asset:
        response.asset_symbol = rating.asset.symbol
        response.asset_name = rating.asset.name

    return response


@router.put("/assets/{asset_id}", response_model=AssetRatingResponse)
async def update_asset_rating(
    asset_id: int,
    data: AssetRatingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing asset rating."""
    result = await db.execute(
        select(AssetRating)
        .options(selectinload(AssetRating.asset))
        .where(AssetRating.asset_id == asset_id)
    )
    rating = result.scalar_one_or_none()

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found for this asset")

    # Update issuer scores if provided
    if data.issuer:
        rating.issuer_social_score = data.issuer.social_score
        rating.issuer_decentralization_score = data.issuer.decentralization_score
        rating.issuer_technical_score = data.issuer.technical_score

    # Update credit score if provided
    if data.credit:
        rating.credit_risk_score = data.credit.credit_risk_score

    # Update operational scores if provided
    if data.operational:
        rating.operational_lindy_score = data.operational.lindy_score
        rating.operational_audit_score = data.operational.audit_score
        rating.operational_transparency_score = data.operational.transparency_score

    # Update metadata if provided
    if data.rated_by:
        rating.rated_by = data.rated_by
    if data.rating_notes is not None:
        rating.rating_notes = data.rating_notes

    # Recompute ratings
    computed = calculator.compute_full_asset_rating(
        issuer_social=rating.issuer_social_score,
        issuer_decentralization=rating.issuer_decentralization_score,
        issuer_technical=rating.issuer_technical_score,
        credit_risk=rating.credit_risk_score,
        operational_lindy=rating.operational_lindy_score,
        operational_audit=rating.operational_audit_score,
        operational_transparency=rating.operational_transparency_score,
    )

    rating.issuer_risk_rating = computed["issuer_risk_rating"]
    rating.operational_risk_rating = computed["operational_risk_rating"]
    rating.asset_rating = computed["asset_rating"]
    rating.vault_eligibility = computed["vault_eligibility"]

    await db.flush()
    await db.refresh(rating)

    response = AssetRatingResponse.model_validate(rating)
    if rating.asset:
        response.asset_symbol = rating.asset.symbol
        response.asset_name = rating.asset.name

    return response


@router.delete("/assets/{asset_id}", status_code=204)
async def delete_asset_rating(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an asset rating."""
    result = await db.execute(
        select(AssetRating).where(AssetRating.asset_id == asset_id)
    )
    rating = result.scalar_one_or_none()

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found for this asset")

    await db.delete(rating)
