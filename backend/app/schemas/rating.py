"""Rating schemas with detailed field descriptions."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IssuerRiskInput(BaseModel):
    """Issuer risk assessment input."""

    social_score: int = Field(
        ...,
        ge=1,
        le=6,
        description="""
社会性评分 (1=AA最好, 6=C最差):
1-AA: 受监管实体，完整牌照，知名机构
2-A: 已识别团队，部分监管，良好声誉
3-BB: 团队公开，无监管但透明
4-B: 团队部分公开，有限透明度
5-CC: 匿名团队，仅多签身份
6-C: 完全匿名，无法追踪
""",
    )
    decentralization_score: int = Field(
        ...,
        ge=1,
        le=6,
        description="""
去中心化评分:
1-AA: 完全去中心化DAO，广泛代币分布，活跃治理
2-A: DAO治理，合理分布，定期投票
3-BB: 有治理机制，但集中度较高
4-B: 有限治理，少数人控制
5-CC: 名义上的DAO，实际中心化
6-C: 完全中心化，无治理
""",
    )
    technical_score: int = Field(
        ...,
        ge=1,
        le=6,
        description="""
技术性评分:
1-AA: 核心合约不可变，无管理员权限
2-A: 不可变合约，仅有限参数可调
3-BB: 可升级但有时间锁(7天+)
4-B: 可升级，短时间锁(1-7天)
5-CC: 可升级，无时间锁
6-C: 完全可控，可随时修改
""",
    )


class CreditRiskInput(BaseModel):
    """Credit risk assessment input."""

    credit_risk_score: int = Field(
        ...,
        ge=1,
        le=6,
        description="""
信用风险评分:
1-AA: 最高质量，如USDC/USDT (受监管发行人)
2-A: 高质量，如DAI (超额抵押，久经考验)
3-BB: 中等，如LST (stETH, cbETH)
4-B: 较高风险，如LRT或新兴稳定币
5-CC: 高风险，如算法稳定币或新协议
6-C: 极高风险，历史有问题或设计缺陷
""",
    )


class OperationalRiskInput(BaseModel):
    """Operational risk assessment input."""

    lindy_score: int = Field(
        ...,
        ge=1,
        le=6,
        description="""
Lindy效应评分:
1-AA: 3年+运营，$1B+ TVL，零安全事故
2-A: 2年+运营，$500M+ TVL，无重大事故
3-BB: 1年+运营，$100M+ TVL
4-B: 6个月+运营，$50M+ TVL
5-CC: 3个月+运营，或TVL较低
6-C: 新协议，未经验证
""",
    )
    audit_score: int = Field(
        ...,
        ge=1,
        le=6,
        description="""
审计评分:
1-AA: 3+顶级审计，活跃Bug Bounty ($1M+)
2-A: 2+知名审计，有Bug Bounty
3-BB: 1+审计，已修复所有问题
4-B: 有审计但有未解决问题
5-CC: 仅有一次审计或审计公司不知名
6-C: 无审计
""",
    )
    transparency_score: int = Field(
        ...,
        ge=1,
        le=6,
        description="""
经济透明度评分:
1-AA: 完全链上可验证，实时储备证明
2-A: 链上数据+定期报告
3-BB: 定期第三方审计报告
4-B: 仅有团队自行报告
5-CC: 有限透明度
6-C: 不透明
""",
    )


class AssetRatingCreate(BaseModel):
    """Schema for creating an asset rating."""

    asset_id: int
    issuer: IssuerRiskInput
    credit: CreditRiskInput
    operational: OperationalRiskInput
    rating_notes: Optional[str] = Field(None, max_length=2000)
    rated_by: str = Field(..., max_length=100)


class AssetRatingUpdate(BaseModel):
    """Schema for updating an asset rating."""

    issuer: Optional[IssuerRiskInput] = None
    credit: Optional[CreditRiskInput] = None
    operational: Optional[OperationalRiskInput] = None
    rating_notes: Optional[str] = Field(None, max_length=2000)
    rated_by: Optional[str] = Field(None, max_length=100)


class AssetRatingResponse(BaseModel):
    """Schema for asset rating response."""

    id: int
    asset_id: int
    asset_symbol: Optional[str] = None
    asset_name: Optional[str] = None

    # Raw scores
    issuer_social_score: Optional[int] = None
    issuer_decentralization_score: Optional[int] = None
    issuer_technical_score: Optional[int] = None
    credit_risk_score: Optional[int] = None
    operational_lindy_score: Optional[int] = None
    operational_audit_score: Optional[int] = None
    operational_transparency_score: Optional[int] = None

    # Computed ratings
    issuer_risk_rating: Optional[str] = None
    operational_risk_rating: Optional[str] = None
    asset_rating: Optional[str] = None
    vault_eligibility: Optional[str] = None

    # Metadata
    rated_by: Optional[str] = None
    rating_notes: Optional[str] = None
    rated_at: datetime

    model_config = {"from_attributes": True}


class RatingListResponse(BaseModel):
    """Schema for rating list response."""

    items: list[AssetRatingResponse]
    total: int
    page: int
    size: int
