"""Alert API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.database import get_db
from app.models import Asset, Protocol, AlertConfig, AlertHistory
from app.schemas.alert import (
    AlertConfigCreate,
    AlertConfigUpdate,
    AlertConfigResponse,
    AlertConfigListResponse,
    AlertHistoryResponse,
    AlertHistoryListResponse,
    AlertTestRequest,
)
from app.exceptions import NotFoundError, ValidationError, ExternalServiceError
from app.dependencies import get_telegram_service
from app.services.alert_service import TelegramService

router = APIRouter()


@router.get("/configs", response_model=AlertConfigListResponse)
async def list_alert_configs(
    is_active: Optional[bool] = Query(None),
    alert_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all alert configurations."""
    query = select(AlertConfig).options(
        selectinload(AlertConfig.asset),
        selectinload(AlertConfig.protocol),
    )

    if is_active is not None:
        query = query.where(AlertConfig.is_active == is_active)
    if alert_type:
        query = query.where(AlertConfig.alert_type == alert_type)

    query = query.order_by(AlertConfig.created_at.desc())

    result = await db.execute(query)
    configs = result.scalars().all()

    items = []
    for config in configs:
        response = AlertConfigResponse.model_validate(config)
        if config.asset:
            response.asset_symbol = config.asset.symbol
        if config.protocol:
            response.protocol_name = config.protocol.name
        # Convert Decimal to float for JSON serialization
        if config.threshold_percent:
            response.threshold_percent = float(config.threshold_percent)
        items.append(response)

    return AlertConfigListResponse(items=items, total=len(items))


@router.post("/configs", response_model=AlertConfigResponse, status_code=201)
async def create_alert_config(
    data: AlertConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new alert configuration."""
    # Validate asset if provided
    if data.asset_id:
        result = await db.execute(
            select(Asset).where(Asset.id == data.asset_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundError("Asset", data.asset_id)

    # Validate protocol if provided
    if data.protocol_id:
        result = await db.execute(
            select(Protocol).where(Protocol.id == data.protocol_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundError("Protocol", data.protocol_id)

    config = AlertConfig(
        name=data.name,
        alert_type=data.alert_type,
        asset_id=data.asset_id,
        protocol_id=data.protocol_id,
        threshold_percent=data.threshold_percent,
        telegram_chat_id=data.telegram_chat_id,
        cooldown_minutes=data.cooldown_minutes,
    )

    db.add(config)
    await db.flush()
    await db.refresh(config)

    return AlertConfigResponse.model_validate(config)


@router.get("/configs/{config_id}", response_model=AlertConfigResponse)
async def get_alert_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single alert configuration."""
    result = await db.execute(
        select(AlertConfig)
        .options(
            joinedload(AlertConfig.asset),
            joinedload(AlertConfig.protocol),
        )
        .where(AlertConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise NotFoundError("AlertConfig", config_id)

    response = AlertConfigResponse.model_validate(config)
    if config.asset:
        response.asset_symbol = config.asset.symbol
    if config.protocol:
        response.protocol_name = config.protocol.name

    return response


@router.put("/configs/{config_id}", response_model=AlertConfigResponse)
async def update_alert_config(
    config_id: int,
    data: AlertConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an alert configuration."""
    result = await db.execute(
        select(AlertConfig).where(AlertConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise NotFoundError("AlertConfig", config_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.flush()
    await db.refresh(config)

    return AlertConfigResponse.model_validate(config)


@router.delete("/configs/{config_id}", status_code=204)
async def delete_alert_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an alert configuration."""
    result = await db.execute(
        select(AlertConfig).where(AlertConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise NotFoundError("AlertConfig", config_id)

    await db.delete(config)


@router.post("/configs/{config_id}/test")
async def test_alert(
    config_id: int,
    data: AlertTestRequest = AlertTestRequest(),
    db: AsyncSession = Depends(get_db),
    telegram: TelegramService = Depends(get_telegram_service),
):
    """Test an alert configuration by sending a test message."""
    result = await db.execute(
        select(AlertConfig).where(AlertConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise NotFoundError("AlertConfig", config_id)

    if not config.telegram_chat_id:
        raise ValidationError("No Telegram chat ID configured", field="telegram_chat_id")

    success = await telegram.send_alert(
        severity="low",
        title=f"Test Alert: {config.name}",
        message=data.message,
        chat_id=config.telegram_chat_id,
    )

    if not success:
        raise ExternalServiceError("Telegram", "Failed to send test alert")

    return {"status": "success", "message": "Test alert sent successfully"}


@router.get("/history", response_model=AlertHistoryListResponse)
async def list_alert_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    config_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    acknowledged: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List alert history with optional filtering."""
    query = select(AlertHistory).options(selectinload(AlertHistory.config))

    if config_id:
        query = query.where(AlertHistory.alert_config_id == config_id)
    if severity:
        query = query.where(AlertHistory.severity == severity)
    if acknowledged is not None:
        query = query.where(AlertHistory.acknowledged == acknowledged)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(AlertHistory.triggered_at.desc())

    result = await db.execute(query)
    history = result.scalars().all()

    items = []
    for record in history:
        response = AlertHistoryResponse.model_validate(record)
        if record.config:
            response.alert_name = record.config.name
        items.append(response)

    return AlertHistoryListResponse(
        items=items,
        total=total or 0,
        page=page,
        size=size,
    )


@router.put("/history/{history_id}/acknowledge")
async def acknowledge_alert(
    history_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge an alert."""
    result = await db.execute(
        select(AlertHistory).where(AlertHistory.id == history_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundError("AlertHistory", history_id)

    record.acknowledged = True
    await db.flush()

    return {"status": "success", "message": "Alert acknowledged"}
