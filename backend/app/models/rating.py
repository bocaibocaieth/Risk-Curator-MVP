"""Rating models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Numeric, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.protocol import Protocol


class AssetRating(Base):
    """Asset rating model - Layer 1 & 2 of the rating framework."""

    __tablename__ = "asset_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        unique=True,
    )

    # Layer 1: Issuer Risk Scores (1-6)
    issuer_social_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("issuer_social_score BETWEEN 1 AND 6"),
    )
    issuer_decentralization_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("issuer_decentralization_score BETWEEN 1 AND 6"),
    )
    issuer_technical_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("issuer_technical_score BETWEEN 1 AND 6"),
    )

    # Layer 1: Credit Risk Score
    credit_risk_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("credit_risk_score BETWEEN 1 AND 6"),
    )

    # Layer 1: Operational Risk Scores
    operational_lindy_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("operational_lindy_score BETWEEN 1 AND 6"),
    )
    operational_audit_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("operational_audit_score BETWEEN 1 AND 6"),
    )
    operational_transparency_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("operational_transparency_score BETWEEN 1 AND 6"),
    )

    # Computed Ratings (AA, A, BB, B, CC, C)
    issuer_risk_rating: Mapped[Optional[str]] = mapped_column(String(2))
    operational_risk_rating: Mapped[Optional[str]] = mapped_column(String(2))
    asset_rating: Mapped[Optional[str]] = mapped_column(String(2))

    # Vault Eligibility
    vault_eligibility: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Prime, High Yield, Constrained, Excluded",
    )

    # Metadata
    rated_by: Mapped[Optional[str]] = mapped_column(String(100))
    rating_notes: Mapped[Optional[str]] = mapped_column(Text)
    rated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="rating")

    def __repr__(self) -> str:
        return f"<AssetRating asset_id={self.asset_id} rating={self.asset_rating}>"


class MarketRating(Base):
    """Market rating model - Layer 3 for lending markets (e.g., Morpho)."""

    __tablename__ = "market_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocol_id: Mapped[int] = mapped_column(
        ForeignKey("protocols.id", ondelete="CASCADE"),
    )
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        comment="Collateral asset",
    )
    loan_asset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"),
        comment="Loan asset",
    )

    # Layer 3: Market Risk Scores
    oracle_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("oracle_score BETWEEN 1 AND 6"),
    )
    liquidity_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("liquidity_score BETWEEN 1 AND 6"),
    )
    price_fluctuation_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("price_fluctuation_score BETWEEN 1 AND 6"),
    )

    # LLTV Configuration
    lltv_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    lltv_adjustment: Mapped[int] = mapped_column(Integer, default=0)

    # Computed Ratings
    credit_enhancement_rating: Mapped[Optional[str]] = mapped_column(String(2))
    market_rating: Mapped[Optional[str]] = mapped_column(String(2))
    final_market_rating: Mapped[Optional[str]] = mapped_column(String(2))

    # Market Address
    market_address: Mapped[Optional[str]] = mapped_column(String(66))

    # Metadata
    rated_by: Mapped[Optional[str]] = mapped_column(String(100))
    rated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    protocol: Mapped["Protocol"] = relationship(back_populates="market_ratings")
    collateral_asset: Mapped["Asset"] = relationship(foreign_keys=[asset_id])
    loan_asset: Mapped[Optional["Asset"]] = relationship(foreign_keys=[loan_asset_id])

    def __repr__(self) -> str:
        return f"<MarketRating protocol_id={self.protocol_id} rating={self.final_market_rating}>"
