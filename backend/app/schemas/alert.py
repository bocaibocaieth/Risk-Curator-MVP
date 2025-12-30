"""Alert schemas."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


AlertType = Literal["price_deviation", "depeg", "tvl_drop", "liquidity"]
Severity = Literal["low", "medium", "high", "critical"]


class AlertConfigCreate(BaseModel):
    """Schema for creating an alert configuration."""

    name: str = Field(..., max_length=100, examples=["USDC Depeg Alert"])
    alert_type: AlertType = Field(
        ...,
        description="""
告警类型:
- price_deviation: 价格偏离基准
- depeg: 稳定币脱锚
- tvl_drop: TVL下降
- liquidity: 流动性不足
""",
    )
    asset_id: Optional[int] = Field(None, description="Target asset ID")
    protocol_id: Optional[int] = Field(None, description="Target protocol ID")
    threshold_percent: float = Field(
        ...,
        gt=0,
        le=100,
        description="Trigger threshold percentage",
        examples=[1.0, 5.0],
    )
    telegram_chat_id: str = Field(
        ...,
        description="Telegram Chat ID (group or personal)",
    )
    cooldown_minutes: int = Field(
        default=60,
        ge=1,
        description="Cooldown period in minutes to avoid repeated alerts",
    )


class AlertConfigUpdate(BaseModel):
    """Schema for updating an alert configuration."""

    name: Optional[str] = Field(None, max_length=100)
    threshold_percent: Optional[float] = Field(None, gt=0, le=100)
    telegram_chat_id: Optional[str] = None
    cooldown_minutes: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class AlertConfigResponse(BaseModel):
    """Schema for alert configuration response."""

    id: int
    name: str
    alert_type: str
    asset_id: Optional[int] = None
    asset_symbol: Optional[str] = None
    protocol_id: Optional[int] = None
    protocol_name: Optional[str] = None
    threshold_percent: Optional[float] = None
    telegram_chat_id: Optional[str] = None
    cooldown_minutes: int
    is_active: bool
    last_triggered_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertConfigListResponse(BaseModel):
    """Schema for alert config list response."""

    items: list[AlertConfigResponse]
    total: int


class AlertHistoryResponse(BaseModel):
    """Schema for alert history response."""

    id: int
    alert_config_id: int
    alert_name: Optional[str] = None
    triggered_value: Optional[float] = None
    message: Optional[str] = None
    severity: Optional[str] = None
    acknowledged: bool
    triggered_at: datetime

    model_config = {"from_attributes": True}


class AlertHistoryListResponse(BaseModel):
    """Schema for alert history list response."""

    items: list[AlertHistoryResponse]
    total: int
    page: int
    size: int


class AlertTestRequest(BaseModel):
    """Schema for testing an alert."""

    message: str = Field(
        default="This is a test alert from Risk Curator",
        max_length=500,
    )
