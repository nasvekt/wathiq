"""
Expatriate Nationality Diversity Cap Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Checks that no single foreign nationality exceeds 40% of total
expatriate workforce (applies to companies with 100+ employees).
Warning at 38%.
"""

from decimal import Decimal, ROUND_HALF_UP
from collections import Counter
from app.engines.rules_fetcher import get_rule


def check_diversity_cap(
    employees: list[dict],
) -> dict:
    """
    Check expatriate nationality diversity.

    Args:
        employees: List of dicts with keys:
            - nationality: str
            - is_saudi: bool

    Returns:
        {
            "applicable": bool,
            "total_expatriates": int,
            "nationality_breakdown": {nationality: count},
            "nationality_percentages": {nationality: pct},
            "exceeded_cap": bool,
            "warning_nationalities": list[str],
            "flags": list[str],
        }
    """
    cap_pct = Decimal(str(get_rule("diversity_cap_pct")))
    warning_pct = Decimal(str(get_rule("diversity_warning_pct")))
    min_headcount = int(get_rule("diversity_min_headcount"))

    total_employees = len(employees)
    if total_employees < min_headcount:
        return {
            "applicable": False,
            "total_expatriates": 0,
            "nationality_breakdown": {},
            "nationality_percentages": {},
            "exceeded_cap": False,
            "warning_nationalities": [],
            "flags": [],
        }

    # Count expatriates by nationality
    expat_nationalities = []
    for emp in employees:
        nat = emp.get("nationality", "").strip()
        is_saudi = emp.get("is_saudi", False)
        if nat and not is_saudi:
            expat_nationalities.append(nat)

    total_expatriates = len(expat_nationalities)
    if total_expatriates == 0:
        return {
            "applicable": True,
            "total_expatriates": 0,
            "nationality_breakdown": {},
            "nationality_percentages": {},
            "exceeded_cap": False,
            "warning_nationalities": [],
            "flags": [],
        }

    counts = Counter(expat_nationalities)
    breakdown = {}
    percentages = {}
    warning_nats = []
    flags = []

    for nat, count in counts.items():
        pct = (Decimal(count) / Decimal(total_expatriates) * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        breakdown[nat] = count
        percentages[nat] = pct

        if pct >= cap_pct * 100:
            warning_nats.append(nat)
            flags.append(f"DIVERSITY_CAP_EXCEEDED:{nat}")
        elif pct >= warning_pct * 100:
            warning_nats.append(nat)
            flags.append(f"DIVERSITY_WARNING:{nat}")

    return {
        "applicable": True,
        "total_expatriates": total_expatriates,
        "nationality_breakdown": breakdown,
        "nationality_percentages": {k: float(v) for k, v in percentages.items()},
        "exceeded_cap": len([f for f in flags if "EXCEEDED" in f]) > 0,
        "warning_nationalities": warning_nats,
        "flags": flags,
    }
