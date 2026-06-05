"""
WPS (Wage Protection System) Calculation Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Calculates:
- Expatriate minimum wage floor check
- Saudi minimum wage check
- Salary variance tolerance (±10% from GOSI contract)
"""

from decimal import Decimal, ROUND_HALF_UP
from app.engines.rules_fetcher import get_rule


def check_wps_floor(
    nationality: str,
    total_gross_wage: Decimal,
) -> dict:
    """
    Check if employee meets WPS minimum wage floor.

    Expatriates: >= SAR 3,200
    Saudis: >= SAR 4,000 (Nitaqat minimum, checked separately)
    """
    is_saudi = nationality and nationality.strip().lower() in ("saudi", "saudi arabia", "sa")

    if is_saudi:
        floor = Decimal(str(get_rule("wps_saudi_min_for_nitaqat")))
    else:
        floor = Decimal(str(get_rule("wps_expatriate_floor")))

    passed = total_gross_wage >= floor

    return {
        "check": "wps_floor",
        "passed": passed,
        "floor": floor,
        "actual": total_gross_wage.quantize(Decimal("0.01")),
        "shortfall": (floor - total_gross_wage).quantize(Decimal("0.01")) if not passed else Decimal("0.00"),
    }


def check_wps_variance(
    paid_gross_wage: Decimal,
    registered_gosi_contract_salary: Decimal,
) -> dict:
    """
    Check if paid gross wage deviates more than ±10% from registered GOSI contract salary.

    Variance (%) = |Paid - Registered| / Registered × 100
    """
    if registered_gosi_contract_salary == 0:
        return {
            "check": "wps_variance",
            "passed": False,
            "variance_pct": Decimal("0.00"),
            "tolerance_pct": Decimal(str(get_rule("wps_variance_tolerance_pct"))) * 100,
            "message": "Registered GOSI contract salary is zero — cannot compute variance",
        }

    tolerance = Decimal(str(get_rule("wps_variance_tolerance_pct")))
    variance = abs(paid_gross_wage - registered_gosi_contract_salary) / registered_gosi_contract_salary
    variance_pct = (variance * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    passed = variance <= tolerance

    return {
        "check": "wps_variance",
        "passed": passed,
        "variance_pct": variance_pct,
        "tolerance_pct": (tolerance * 100).quantize(Decimal("0.01")),
        "paid_gross": paid_gross_wage.quantize(Decimal("0.01")),
        "registered_salary": registered_gosi_contract_salary.quantize(Decimal("0.01")),
    }
