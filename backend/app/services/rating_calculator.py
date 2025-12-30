"""
Rating calculation service based on Steakhouse Financial's Multi-Layer Risk Rating Framework.

Score Scale: 1-6 where 1 is best (AA) and 6 is worst (C)
Grade Scale: AA, A, BB, B, CC, C
"""

from decimal import Decimal
from typing import Tuple

# Score to Grade mapping
SCORE_TO_GRADE = {1: "AA", 2: "A", 3: "BB", 4: "B", 5: "CC", 6: "C"}
GRADE_TO_SCORE = {"AA": 1, "A": 2, "BB": 3, "B": 4, "CC": 5, "C": 6}


def score_to_grade(score: int) -> str:
    """Convert numeric score (1-6) to letter grade."""
    return SCORE_TO_GRADE.get(score, "C")


def grade_to_score(grade: str) -> int:
    """Convert letter grade to numeric score."""
    return GRADE_TO_SCORE.get(grade.upper(), 6)


class RatingCalculator:
    """
    Calculate asset and market ratings based on the multi-layer framework.

    Layer 1: Asset Risk (Issuer + Credit + Operational)
    Layer 2: Platform Risk (for protocols)
    Layer 3: Market Risk (for lending markets)
    """

    @staticmethod
    def calculate_issuer_risk(
        social_score: int,
        decentralization_score: int,
        technical_score: int,
    ) -> str:
        """
        Calculate issuer risk rating.

        Issuer Risk = MIN score (best of the three categories)
        Taking the minimum means we use the BEST score among the categories,
        as lower score = better rating.
        """
        best_score = min(social_score, decentralization_score, technical_score)
        return score_to_grade(best_score)

    @staticmethod
    def calculate_operational_risk(
        lindy_score: int,
        audit_score: int,
        transparency_score: int,
    ) -> str:
        """
        Calculate operational risk rating.

        Operational Risk = MAX score (worst of the three categories)
        Taking the maximum means we use the WORST score among the categories,
        as higher score = worse rating.
        """
        worst_score = max(lindy_score, audit_score, transparency_score)
        return score_to_grade(worst_score)

    @staticmethod
    def calculate_asset_rating(
        issuer_risk_grade: str,
        credit_risk_score: int,
        operational_risk_grade: str,
    ) -> str:
        """
        Calculate final asset rating.

        Asset Rating = MAX score (worst of issuer, credit, operational)
        The final rating is constrained by the weakest dimension.
        """
        issuer_score = grade_to_score(issuer_risk_grade)
        operational_score = grade_to_score(operational_risk_grade)
        worst_score = max(issuer_score, credit_risk_score, operational_score)
        return score_to_grade(worst_score)

    @staticmethod
    def calculate_credit_enhancement(
        price_fluctuation_score: int,
        lltv_percent: Decimal,
    ) -> Tuple[str, int]:
        """
        Calculate credit enhancement from LLTV.

        LLTV adjustment: Lower LLTV provides better credit enhancement.
        - 94.5%+ -> 0 adjustment
        - 90-94.5% -> 1 level improvement
        - 85-90% -> 2 levels improvement
        - 80-85% -> 3 levels improvement
        - 75-80% -> 4 levels improvement
        - <75% -> 5 levels improvement

        Returns: (enhanced_rating, lltv_adjustment)
        """
        lltv = float(lltv_percent)

        if lltv >= 94.5:
            lltv_adjustment = 0
        elif lltv >= 90:
            lltv_adjustment = 1
        elif lltv >= 85:
            lltv_adjustment = 2
        elif lltv >= 80:
            lltv_adjustment = 3
        elif lltv >= 75:
            lltv_adjustment = 4
        else:
            lltv_adjustment = 5

        # Apply adjustment (lower score = better)
        enhanced_score = max(1, price_fluctuation_score - lltv_adjustment)
        return score_to_grade(enhanced_score), lltv_adjustment

    @staticmethod
    def calculate_market_rating(
        oracle_score: int,
        liquidity_score: int,
        credit_enhancement_grade: str,
    ) -> str:
        """
        Calculate market rating.

        Market Rating = MAX score (worst of oracle, liquidity, credit enhancement)
        """
        ce_score = grade_to_score(credit_enhancement_grade)
        worst_score = max(oracle_score, liquidity_score, ce_score)
        return score_to_grade(worst_score)

    @staticmethod
    def calculate_final_market_rating(
        adjusted_asset_grade: str,
        platform_grade: str,
        market_grade: str,
    ) -> str:
        """
        Calculate final market rating.

        Final Rating = MAX score (worst of adjusted asset, platform, market)
        """
        scores = [
            grade_to_score(adjusted_asset_grade),
            grade_to_score(platform_grade),
            grade_to_score(market_grade),
        ]
        worst_score = max(scores)
        return score_to_grade(worst_score)

    @staticmethod
    def get_vault_eligibility(final_rating: str) -> str:
        """
        Determine vault eligibility based on final rating.

        - AA, A: Prime (highest quality, conservative vaults)
        - BB, B: High Yield (moderate risk, yield-focused vaults)
        - CC: Constrained (limited exposure allowed)
        - C: Excluded (not eligible for any vault)
        """
        score = grade_to_score(final_rating)

        if score <= 2:  # AA or A
            return "Prime"
        elif score <= 4:  # BB or B
            return "High Yield"
        elif score == 5:  # CC
            return "Constrained"
        else:  # C
            return "Excluded"

    def compute_full_asset_rating(
        self,
        issuer_social: int,
        issuer_decentralization: int,
        issuer_technical: int,
        credit_risk: int,
        operational_lindy: int,
        operational_audit: int,
        operational_transparency: int,
    ) -> dict:
        """
        Compute all rating components for an asset.

        Returns a dictionary with all computed ratings.
        """
        # Calculate component ratings
        issuer_risk = self.calculate_issuer_risk(
            issuer_social,
            issuer_decentralization,
            issuer_technical,
        )

        operational_risk = self.calculate_operational_risk(
            operational_lindy,
            operational_audit,
            operational_transparency,
        )

        # Calculate final asset rating
        asset_rating = self.calculate_asset_rating(
            issuer_risk,
            credit_risk,
            operational_risk,
        )

        # Determine vault eligibility
        vault_eligibility = self.get_vault_eligibility(asset_rating)

        return {
            "issuer_risk_rating": issuer_risk,
            "operational_risk_rating": operational_risk,
            "asset_rating": asset_rating,
            "vault_eligibility": vault_eligibility,
        }
