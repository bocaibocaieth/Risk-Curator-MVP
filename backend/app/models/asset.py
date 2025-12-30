"""Asset model."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.rating import AssetRating
    from app.models.price import PriceHistory
    from app.models.alert import AlertConfig


class Asset(Base):
    """Asset model for tracking DeFi assets."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="stablecoin, lst, lrt, pt, native, rwa",
    )
    chain: Mapped[str] = mapped_column(String(20), default="ethereum")
    contract_address: Mapped[Optional[str]] = mapped_column(String(66))
    coingecko_id: Mapped[Optional[str]] = mapped_column(String(100))
    defillama_id: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    rating: Mapped[Optional["AssetRating"]] = relationship(
        back_populates="asset",
        uselist=False,
    )
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="asset",
    )
    alert_configs: Mapped[list["AlertConfig"]] = relationship(
        back_populates="asset",
        foreign_keys="AlertConfig.asset_id",
    )

    def __repr__(self) -> str:
        return f"<Asset {self.symbol} ({self.chain})>"
