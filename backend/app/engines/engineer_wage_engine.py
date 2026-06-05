"""
Saudi Engineer Wage Floor Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Checks if a Saudi employee classified as an engineer (SSCO 2141xx-2149xx)
meets the SAR 7,000 minimum wage floor for full Nitaqat weight.
"""

from decimal import Decimal, ROUND_HALF_UP
from app.engines.rules_fetcher import get_rule


def check_engineer_wage_floor(
    nationality: str,
    ssco_code: str | None,
    basic_salary: Decimal,
) -> dict:
    """
    Check if a Saudi engineer meets the sector-specific wage floor.

    Engineering SSCO codes: 2141xx, 2142xx, 2143xx, 2144xx, 2145xx, 2146xx, 2149xx
    Minimum basic salary for full Nitaqat weight: SAR 7,000

    Returns:
        {
            "is_engineer": bool,
            "ssco_code": str | None,
            "engineer_min_salary": Decimal,
            "meets_floor": bool,
            "wage_floor_applied": str,
            "flags": list[str],
        }
    """
    engineer_prefixes = get_rule("engineer_ssco_prefixes")
    engineer_min = Decimal(str(get_rule("engineer_min_salary")))

    is_saudi = nationality and nationality.strip().lower() in ("saudi", "saudi arabia", "sa")

    # Check if SSCO code is in engineering range
    is_engineer = False
    if ssco_code:
        for prefix in engineer_prefixes:
            if ssco_code.startswith(prefix):
                is_engineer = True
                break

    if not is_engineer:
        return {
            "is_engineer": False,
            "ssco_code": ssco_code,
            "engineer_min_salary": engineer_min,
            "meets_floor": True,  # Not applicable
            "wage_floor_applied": "general_4000",
            "flags": [],
        }

    meets_floor = basic_salary >= engineer_min
    flags = []
    if not meets_floor:
        flags.append("ENGINEER_WAGE_FLOOR_VIOLATION")

    return {
        "is_engineer": True,
        "ssco_code": ssco_code,
        "engineer_min_salary": engineer_min,
        "meets_floor": meets_floor,
        "wage_floor_applied": "engineer_7000",
        "flags": flags,
    }
