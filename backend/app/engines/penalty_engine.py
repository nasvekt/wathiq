"""
Company Health Score Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Calculates a 0-100 health score based on compliance flags.
"""

from decimal import Decimal, ROUND_HALF_UP
from app.engines.rules_fetcher import get_rule


def calculate_health_score(
    blocked_count: int,
    review_count: int,
    red_band: bool,
    iqama_expiring_30_days: int,
    iqama_expired: int,
) -> dict:
    """
    Calculate Company Health Score.

    Start at 100. Subtract:
    - 20 per Blocked record
    - 5 per Review record
    - 25 if in Red band
    - 5 per Iqama expiring within 30 days
    - 10 per expired Iqama
    Floor at 0.
    """
    score = 100
    score -= blocked_count * 20
    score -= review_count * 5
    if red_band:
        score -= 25
    score -= iqama_expiring_30_days * 5
    score -= iqama_expired * 10

    score = max(0, score)

    if score >= 90:
        color = "green"
    elif score >= 70:
        color = "yellow"
    else:
        color = "red"

    return {
        "score": score,
        "color": color,
        "max_score": 100,
        "deductions": {
            "blocked_records": blocked_count * 20,
            "review_records": review_count * 5,
            "yellow_band": 0,
            "red_band": 25 if red_band else 0,
            "iqama_expiring_30d": iqama_expiring_30_days * 5,
            "iqama_expired": iqama_expired * 10,
        },
    }


def calculate_penalty_exposure(
    blocked_count: int,
    review_count: int,
) -> Decimal:
    """
    Estimate financial penalty exposure.

    Conservative estimate:
    - SAR 5,000 per Blocked record
    - SAR 1,500 per Review record
    """
    exposure = (Decimal(blocked_count) * Decimal("5000")) + (
        Decimal(review_count) * Decimal("1500")
    )
    return exposure.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
