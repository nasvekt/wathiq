"""
Housing Allowance Parity Check Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Checks that every employee has a non-zero housing allowance,
and flags if it's below 10% of basic salary.
"""

from decimal import Decimal, ROUND_HALF_UP
from app.engines.rules_fetcher import get_rule


def check_housing_allowance(
    basic_salary: Decimal,
    housing_allowance: Decimal,
) -> dict:
    """
    Check housing allowance compliance.

    Rules:
    - Must be > 0
    - Recommended minimum: 10% of basic salary
    """
    min_pct = Decimal(str(get_rule("housing_min_pct_of_basic")))
    recommended_min = (basic_salary * min_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    has_housing = housing_allowance > 0
    meets_minimum = housing_allowance >= recommended_min

    flags = []
    if not has_housing:
        flags.append("HOUSING_ZERO")
    elif not meets_minimum:
        flags.append("HOUSING_BELOW_RECOMMENDED")

    return {
        "check": "housing_allowance",
        "passed": has_housing,
        "housing_allowance": housing_allowance.quantize(Decimal("0.01")),
        "recommended_minimum": recommended_min,
        "actual_pct_of_basic": (
            (housing_allowance / basic_salary * 100).quantize(Decimal("0.01"))
            if basic_salary > 0
            else Decimal("0.00")
        ),
        "flags": flags,
    }
