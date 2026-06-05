"""
Qiwa Digital Labor Contract Window Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Checks if an employee's digital labor contract has been published
on Qiwa within 30 calendar days of hire date.
Warning at day 25, violation at day 30.
"""

from datetime import date
from app.engines.rules_fetcher import get_rule


def check_contract_window(
    hire_date: date | None,
    contract_published: bool = False,
    contract_published_date: date | None = None,
    reference_date: date | None = None,
) -> dict:
    """
    Check Qiwa digital labor contract publication window.

    Rules:
    - Contract must be published within 30 calendar days of hire
    - Warning triggered at day 25
    - Violation at day 30

    Returns:
        {
            "has_hire_date": bool,
            "days_elapsed": int | None,
            "window_days": int,
            "warning_day": int,
            "contract_published": bool,
            "status": "clear" | "warning" | "violation" | "unknown",
            "flags": list[str],
        }
    """
    window_days = int(get_rule("qiwa_contract_window_days"))
    warning_day = int(get_rule("qiwa_contract_warning_day"))

    if not hire_date:
        return {
            "has_hire_date": False,
            "days_elapsed": None,
            "window_days": window_days,
            "warning_day": warning_day,
            "contract_published": contract_published,
            "status": "unknown",
            "flags": [],
        }

    ref = reference_date or date.today()
    days_elapsed = (ref - hire_date).days

    if contract_published:
        return {
            "has_hire_date": True,
            "days_elapsed": days_elapsed,
            "window_days": window_days,
            "warning_day": warning_day,
            "contract_published": True,
            "status": "clear",
            "flags": [],
        }

    flags = []
    if days_elapsed >= window_days:
        status = "violation"
        flags.append("QIWA_CONTRACT_WINDOW_VIOLATION")
    elif days_elapsed >= warning_day:
        status = "warning"
        flags.append("QIWA_CONTRACT_WINDOW_WARNING")
    else:
        status = "clear"

    return {
        "has_hire_date": True,
        "days_elapsed": days_elapsed,
        "window_days": window_days,
        "warning_day": warning_day,
        "contract_published": contract_published,
        "status": status,
        "flags": flags,
    }
