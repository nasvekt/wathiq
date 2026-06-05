"""
Iqama Expiry Monitoring Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Tracks Iqama expiry dates and generates alerts at 90, 60, 30, and 7 days.
"""

from datetime import date, timedelta
from app.engines.rules_fetcher import get_rule


def check_iqama_expiry(
    iqama_expiry_date: date | None,
    reference_date: date | None = None,
) -> dict:
    """
    Check Iqama expiry status.

    Returns:
        {
            "has_expiry_date": bool,
            "expiry_date": date | None,
            "days_remaining": int | None,
            "status": "valid" | "at_risk" | "expired" | "unknown",
            "alert_triggered": bool,
            "alert_level": 90 | 60 | 30 | 7 | "expired" | None,
        }
    """
    if not iqama_expiry_date:
        return {
            "has_expiry_date": False,
            "expiry_date": None,
            "days_remaining": None,
            "status": "unknown",
            "alert_triggered": False,
            "alert_level": None,
        }

    ref = reference_date or date.today()
    days_remaining = (iqama_expiry_date - ref).days
    alert_days = sorted(get_rule("iqama_expiry_alert_days"), reverse=True)

    if days_remaining < 0:
        return {
            "has_expiry_date": True,
            "expiry_date": iqama_expiry_date,
            "days_remaining": days_remaining,
            "status": "expired",
            "alert_triggered": True,
            "alert_level": "expired",
        }

    # Find the closest alert threshold that's been crossed
    alert_level = None
    for threshold in alert_days:
        if days_remaining <= threshold:
            alert_level = threshold

    status = "at_risk" if days_remaining <= alert_days[-1] else "valid"

    return {
        "has_expiry_date": True,
        "expiry_date": iqama_expiry_date,
        "days_remaining": days_remaining,
        "status": status,
        "alert_triggered": alert_level is not None,
        "alert_level": alert_level,
    }
