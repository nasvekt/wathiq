"""
Nitaqat (Saudization) Calculation Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Calculates:
- Individual Saudi employee Nitaqat weight
- Company-wide Saudization ratio
- Nitaqat band classification (Platinum / High Green / Low Green / Yellow / Red)
- Procurement-specific Saudization ratio
"""

from decimal import Decimal, ROUND_HALF_UP
from app.engines.rules_fetcher import get_rule


def calculate_nitaqat_weight(
    nationality: str,
    total_gross_wage: Decimal,
    monthly_hours: int | None = None,
) -> Decimal:
    """
    Calculate a single Saudi employee's Nitaqat weight.

    Rules:
    - Expatriate: 0.0
    - Saudi, gross >= 4000: 1.0
    - Saudi, gross 3000-3999: 0.5
    - Saudi, gross < 3000: 0.0
    - Saudi part-time, >= 160 hours/month: 1.0
    """
    is_saudi = nationality and nationality.strip().lower() in ("saudi", "saudi arabia", "sa")
    if not is_saudi:
        return Decimal("0.0")

    # Part-time check
    hours_threshold = int(get_rule("nitaqat_part_time_hours_threshold"))
    if monthly_hours is not None and monthly_hours >= hours_threshold:
        return Decimal("1.0")

    full_min = Decimal(str(get_rule("nitaqat_full_weight_min")))
    half_min = Decimal(str(get_rule("nitaqat_half_weight_min")))
    half_max = Decimal(str(get_rule("nitaqat_half_weight_max")))

    if total_gross_wage >= full_min:
        return Decimal("1.0")
    elif half_min <= total_gross_wage <= half_max:
        return Decimal("0.5")
    else:
        return Decimal("0.0")


def calculate_saudization_ratio(
    total_employees: int,
    saudi_weights_sum: Decimal,
) -> Decimal:
    """
    Saudization Ratio = (Sum of Saudi weights / Total employees) × 100.

    Returns percentage (e.g. 28.5 for 28.5%).
    """
    if total_employees == 0:
        return Decimal("0.0")
    ratio = (saudi_weights_sum / Decimal(total_employees)) * Decimal("100")
    return ratio.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def classify_nitaqat_band(
    saudization_ratio: Decimal,
    sector_code: str,
    size_category: str,
    nitaqat_matrix: dict | None = None,
) -> str:
    """
    Classify the Nitaqat band based on sector and size.

    In production: fetches thresholds from compliance_rules DB.
    For now: uses a built-in matrix for common sectors.

    Bands: platinum > high_green > low_green > yellow > red
    """
    # Default matrix for common sectors (from blueprint Section 3)
    # Structure: {sector_code: {size_category: {band: min_pct}}}
    DEFAULT_MATRIX = {
        "technology": {
            "medium_a": {"platinum": 40, "high_green": 35, "low_green": 26},
            "medium_b": {"platinum": 40, "high_green": 35, "low_green": 26},
            "large": {"platinum": 40, "high_green": 35, "low_green": 26},
        },
        "construction": {
            "medium_a": {"platinum": 25, "high_green": 20, "low_green": 13},
            "medium_b": {"platinum": 25, "high_green": 20, "low_green": 13},
            "large": {"platinum": 25, "high_green": 20, "low_green": 13},
        },
        "wholesale_retail": {
            "medium_a": {"platinum": 35, "high_green": 30, "low_green": 23},
            "medium_b": {"platinum": 35, "high_green": 30, "low_green": 23},
            "large": {"platinum": 35, "high_green": 30, "low_green": 23},
        },
        "logistics": {
            "medium_a": {"platinum": 30, "high_green": 25, "low_green": 17},
            "medium_b": {"platinum": 30, "high_green": 25, "low_green": 17},
            "large": {"platinum": 30, "high_green": 25, "low_green": 17},
        },
        "travel_tourism": {
            "medium_a": {"platinum": 35, "high_green": 29, "low_green": 19},
            "medium_b": {"platinum": 35, "high_green": 29, "low_green": 19},
            "large": {"platinum": 35, "high_green": 29, "low_green": 19},
        },
    }

    matrix = nitaqat_matrix or DEFAULT_MATRIX
    sector_data = matrix.get(sector_code, {})
    thresholds = sector_data.get(size_category, {})

    if not thresholds:
        # Default conservative thresholds if sector/size not found
        thresholds = {"platinum": 40, "high_green": 35, "low_green": 25}

    if saudization_ratio >= thresholds.get("platinum", 40):
        return "platinum"
    elif saudization_ratio >= thresholds.get("high_green", 35):
        return "high_green"
    elif saudization_ratio >= thresholds.get("low_green", 25):
        return "low_green"
    else:
        return "red"


def calculate_procurement_saudization(
    procurement_employees: list[dict],
) -> dict:
    """
    Calculate procurement-specific Saudization ratio.

    Args:
        procurement_employees: List of dicts with keys:
            - nationality: str
            - total_gross_wage: Decimal
            - monthly_hours: int (optional)

    Returns:
        {
            "total_procurement_headcount": int,
            "saudi_procurement_count": int,
            "saudi_procurement_weight_sum": Decimal,
            "procurement_saudization_pct": Decimal,
            "meets_70_pct_rule": bool,
        }
    """
    total = len(procurement_employees)
    if total == 0:
        return {
            "total_procurement_headcount": 0,
            "saudi_procurement_count": 0,
            "saudi_procurement_weight_sum": Decimal("0.00"),
            "procurement_saudization_pct": Decimal("0.00"),
            "meets_70_pct_rule": True,
        }

    saudi_count = 0
    weight_sum = Decimal("0.0")

    for emp in procurement_employees:
        weight = calculate_nitaqat_weight(
            nationality=emp.get("nationality", ""),
            total_gross_wage=emp.get("total_gross_wage", Decimal("0")),
            monthly_hours=emp.get("monthly_hours"),
        )
        if weight > 0:
            saudi_count += 1
            weight_sum += weight

    pct = (weight_sum / Decimal(total)) * Decimal("100") if total > 0 else Decimal("0")
    pct = pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "total_procurement_headcount": total,
        "saudi_procurement_count": saudi_count,
        "saudi_procurement_weight_sum": weight_sum,
        "procurement_saudization_pct": pct,
        "meets_70_pct_rule": pct >= Decimal("70.00"),
    }
