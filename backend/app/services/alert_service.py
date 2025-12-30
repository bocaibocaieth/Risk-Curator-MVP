"""Telegram alert service."""

import httpx
from typing import Optional
from datetime import datetime

from app.config import settings


class TelegramService:
    """Telegram bot service for sending alerts."""

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.default_chat_id = settings.telegram_default_chat_id

    async def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "HTML",
    ) -> bool:
        """Send a message via Telegram bot."""
        if not self.bot_token:
            print("Telegram bot token not configured")
            return False

        target_chat_id = chat_id or self.default_chat_id
        if not target_chat_id:
            print("No Telegram chat ID provided")
            return False

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": target_chat_id,
                        "text": text,
                        "parse_mode": parse_mode,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"Telegram send error: {e}")
                return False

    async def send_alert(
        self,
        severity: str,
        title: str,
        message: str,
        chat_id: Optional[str] = None,
    ) -> bool:
        """Send a formatted alert message."""
        emoji_map = {
            "low": "ℹ️",
            "medium": "⚠️",
            "high": "🚨",
            "critical": "🔴",
        }
        emoji = emoji_map.get(severity, "📢")

        formatted_message = (
            f"{emoji} <b>{title}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{message}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )

        return await self.send_message(formatted_message, chat_id)


class AlertService:
    """Alert management service."""

    def __init__(self):
        self.telegram = TelegramService()

    async def send_telegram_alert(
        self,
        chat_id: str,
        message: str,
        severity: str = "medium",
    ) -> bool:
        """Send a Telegram alert."""
        return await self.telegram.send_alert(
            severity=severity,
            title="Risk Monitor Alert",
            message=message,
            chat_id=chat_id,
        )

    async def send_price_alert(
        self,
        asset_symbol: str,
        current_price: float,
        threshold: float,
        alert_type: str,
        chat_id: Optional[str] = None,
    ) -> bool:
        """Send a price-related alert."""
        if alert_type == "depeg":
            deviation = abs(1 - current_price) * 100
            message = (
                f"<b>资产:</b> {asset_symbol}\n"
                f"<b>当前价格:</b> ${current_price:.6f}\n"
                f"<b>脱锚程度:</b> {deviation:.4f}%\n"
                f"<b>告警阈值:</b> {threshold}%"
            )
            severity = "high" if deviation > 2 else "medium"
        else:
            message = (
                f"<b>资产:</b> {asset_symbol}\n"
                f"<b>当前价格:</b> ${current_price:.4f}\n"
                f"<b>触发条件:</b> {alert_type}"
            )
            severity = "medium"

        return await self.telegram.send_alert(
            severity=severity,
            title=f"价格告警 - {asset_symbol}",
            message=message,
            chat_id=chat_id,
        )

    async def send_system_alert(
        self,
        title: str,
        message: str,
        severity: str = "low",
    ) -> bool:
        """Send a system alert."""
        return await self.telegram.send_alert(
            severity=severity,
            title=title,
            message=message,
        )
