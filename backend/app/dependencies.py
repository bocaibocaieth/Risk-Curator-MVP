"""FastAPI dependencies for dependency injection."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.price_service import PriceService, TVLService
from app.services.alert_service import TelegramService, AlertService
from app.services.monitor_service import MonitorService


# Service singletons (stateless services can be singletons)
_price_service: PriceService | None = None
_tvl_service: TVLService | None = None
_telegram_service: TelegramService | None = None
_alert_service: AlertService | None = None


def get_price_service() -> PriceService:
    """Get PriceService instance."""
    global _price_service
    if _price_service is None:
        _price_service = PriceService()
    return _price_service


def get_tvl_service() -> TVLService:
    """Get TVLService instance."""
    global _tvl_service
    if _tvl_service is None:
        _tvl_service = TVLService()
    return _tvl_service


def get_telegram_service() -> TelegramService:
    """Get TelegramService instance."""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service


def get_alert_service() -> AlertService:
    """Get AlertService instance."""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service


async def get_monitor_service(
    db: AsyncSession = Depends(get_db),
) -> MonitorService:
    """Get MonitorService instance with database session."""
    return MonitorService(db)
