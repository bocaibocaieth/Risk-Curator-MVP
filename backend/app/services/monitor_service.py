"""Monitoring service for price and alert checks."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Asset, PriceHistory, AlertConfig, AlertHistory
from app.services.price_service import PriceService
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)


class MonitorService:
    """Service for monitoring assets and triggering alerts."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.price_service = PriceService()
        self.alert_service = AlertService()

    async def check_price_deviation(
        self,
        asset: Asset,
        current_price: Decimal,
        alert_config: AlertConfig,
    ) -> Optional[str]:
        """Check if price deviates from baseline beyond threshold."""
        # For stablecoins, baseline is $1
        if asset.asset_type == "stablecoin":
            base_price = Decimal("1.0")
        else:
            # Use 24h average as baseline (using SQL AVG for efficiency)
            stmt = select(func.avg(PriceHistory.price_usd)).where(
                PriceHistory.asset_id == asset.id,
                PriceHistory.recorded_at >= datetime.utcnow() - timedelta(hours=24),
            )
            result = await self.db.execute(stmt)
            avg_price = result.scalar()

            if avg_price is None:
                return None

            base_price = Decimal(str(avg_price))

        if base_price == 0:
            return None

        deviation = abs((current_price - base_price) / base_price) * 100

        if deviation >= float(alert_config.threshold_percent or 0):
            direction = "上涨" if current_price > base_price else "下跌"
            return (
                f"⚠️ 价格偏离告警\n"
                f"资产: {asset.symbol}\n"
                f"当前价格: ${current_price:.4f}\n"
                f"基准价格: ${base_price:.4f}\n"
                f"偏离: {direction} {deviation:.2f}%\n"
                f"阈值: {alert_config.threshold_percent}%"
            )

        return None

    async def check_depeg(
        self,
        asset: Asset,
        current_price: Decimal,
        alert_config: AlertConfig,
    ) -> Optional[str]:
        """Check if stablecoin has depegged."""
        if asset.asset_type != "stablecoin":
            return None

        peg_price = Decimal("1.0")
        deviation = abs((current_price - peg_price) / peg_price) * 100

        if deviation >= float(alert_config.threshold_percent or 0):
            return (
                f"🚨 稳定币脱锚告警\n"
                f"资产: {asset.symbol}\n"
                f"当前价格: ${current_price:.6f}\n"
                f"脱锚程度: {deviation:.4f}%\n"
                f"阈值: {alert_config.threshold_percent}%"
            )

        return None

    async def run_monitoring_cycle(self) -> List[str]:
        """Run a complete monitoring cycle."""
        alerts_triggered: List[str] = []

        try:
            # Get all active assets with alert configs preloaded (avoid N+1 queries)
            stmt = (
                select(Asset)
                .where(Asset.is_active == True)
                .options(selectinload(Asset.alert_configs))
            )
            result = await self.db.execute(stmt)
            assets = result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to fetch assets: {e}")
            return alerts_triggered

        for asset in assets:
            try:
                # Fetch current price
                current_price = await self.price_service.get_price(
                    coingecko_id=asset.coingecko_id,
                    chain=asset.chain,
                    contract=asset.contract_address,
                )

                if current_price is None:
                    logger.debug(f"No price available for {asset.symbol}")
                    continue

                # Record price history
                price_record = PriceHistory(
                    asset_id=asset.id,
                    price_usd=current_price,
                    source="coingecko" if asset.coingecko_id else "defillama",
                )
                self.db.add(price_record)

                # Use preloaded alert configs (avoiding N+1 query)
                configs = [c for c in asset.alert_configs if c.is_active]

                for config in configs:
                    try:
                        # Check cooldown
                        if config.last_triggered_at:
                            cooldown_end = config.last_triggered_at + timedelta(
                                minutes=config.cooldown_minutes
                            )
                            if datetime.utcnow() < cooldown_end:
                                continue

                        # Check based on alert type
                        alert_message = None
                        if config.alert_type == "price_deviation":
                            alert_message = await self.check_price_deviation(
                                asset, current_price, config
                            )
                        elif config.alert_type == "depeg":
                            alert_message = await self.check_depeg(
                                asset, current_price, config
                            )

                        if alert_message:
                            # Send alert
                            if config.telegram_chat_id:
                                await self.alert_service.send_telegram_alert(
                                    chat_id=config.telegram_chat_id,
                                    message=alert_message,
                                    severity="high" if config.alert_type == "depeg" else "medium",
                                )

                            # Record alert history
                            history = AlertHistory(
                                alert_config_id=config.id,
                                triggered_value=current_price,
                                message=alert_message,
                                severity="high" if config.alert_type == "depeg" else "medium",
                            )
                            self.db.add(history)

                            # Update last triggered time
                            config.last_triggered_at = datetime.utcnow()
                            alerts_triggered.append(alert_message)
                    except Exception as e:
                        logger.error(
                            f"Error processing alert config",
                            extra={
                                "config_id": config.id,
                                "config_name": config.name,
                                "alert_type": config.alert_type,
                                "asset_symbol": asset.symbol,
                                "error": str(e),
                            },
                        )
                        continue

            except Exception as e:
                logger.error(
                    f"Error monitoring asset",
                    extra={
                        "asset_id": asset.id,
                        "asset_symbol": asset.symbol,
                        "chain": asset.chain,
                        "error": str(e),
                    },
                )
                continue

        # Commit all changes with proper error tracking
        if alerts_triggered:
            try:
                await self.db.commit()
                logger.info(f"Monitoring cycle completed: {len(alerts_triggered)} alerts triggered")
            except Exception as e:
                logger.error(
                    f"Failed to commit monitoring changes",
                    extra={"alerts_count": len(alerts_triggered), "error": str(e)},
                )
                await self.db.rollback()
                # Clear alerts since they weren't persisted
                alerts_triggered.clear()
        else:
            # Still commit price history even if no alerts
            try:
                await self.db.commit()
            except Exception as e:
                logger.error(f"Failed to commit price history: {e}")
                await self.db.rollback()

        return alerts_triggered
