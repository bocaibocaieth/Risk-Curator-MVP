"""Protocol model."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.rating import MarketRating
    from app.models.alert import AlertConfig


class Protocol(Base):
    """Protocol model for tracking DeFi protocols."""

    __tablename__ = "protocols"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="lending, dex, yield, derivatives",
    )
    chain: Mapped[str] = mapped_column(String(20), default="ethereum")
    website: Mapped[Optional[str]] = mapped_column(String(255))
    defillama_id: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    market_ratings: Mapped[list["MarketRating"]] = relationship(
        back_populates="protocol",
    )
    alert_configs: Mapped[list["AlertConfig"]] = relationship(
        back_populates="protocol",
    )

    def __repr__(self) -> str:
        return f"<Protocol {self.name}>"
