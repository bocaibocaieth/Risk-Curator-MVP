"""Alert models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, Text, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.protocol import Protocol


class AlertConfig(Base):
    """Alert configuration model."""

    __tablename__ = "alert_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="price_deviation, tvl_drop, depeg, liquidity",
    )
    asset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"),
    )
    protocol_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("protocols.id", ondelete="SET NULL"),
    )

    # Thresholds
    threshold_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    threshold_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    comparison: Mapped[Optional[str]] = mapped_column(
        String(10),
        comment="gt, lt, deviation",
    )

    # Notification Settings
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    asset: Mapped[Optional["Asset"]] = relationship(
        back_populates="alert_configs",
        foreign_keys=[asset_id],
    )
    protocol: Mapped[Optional["Protocol"]] = relationship(
        back_populates="alert_configs",
    )
    history: Mapped[list["AlertHistory"]] = relationship(
        back_populates="config",
    )

    def __repr__(self) -> str:
        return f"<AlertConfig {self.name} type={self.alert_type}>"


class AlertHistory(Base):
    """Alert history model for tracking triggered alerts."""

    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_config_id: Mapped[int] = mapped_column(
        ForeignKey("alert_configs.id", ondelete="CASCADE"),
    )
    triggered_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    message: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="low, medium, high, critical",
    )
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    config: Mapped["AlertConfig"] = relationship(back_populates="history")

    def __repr__(self) -> str:
        return f"<AlertHistory config_id={self.alert_config_id} severity={self.severity}>"
