"""Price history model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.asset import Asset


class PriceHistory(Base):
    """Price history model for tracking asset prices over time."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
    )
    price_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="coingecko, chainlink, dex",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="price_history")

    # Composite index for efficient time-series queries
    __table_args__ = (
        Index("idx_price_history_asset_time", "asset_id", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<PriceHistory asset_id={self.asset_id} price={self.price_usd}>"
