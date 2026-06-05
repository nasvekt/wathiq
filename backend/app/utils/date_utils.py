"""Wathiq — date utilities (Arabic calendar, KSA timezone)."""
from datetime import date, datetime, timedelta, timezone

KSA_TZ = timezone(timedelta(hours=3))


def today_ksa() -> date:
    """Get today's date in KSA timezone (UTC+3)."""
    return datetime.now(KSA_TZ).date()


def now_ksa() -> datetime:
    """Get current datetime in KSA timezone."""
    return datetime.now(KSA_TZ)


def days_until(target: date) -> int:
    """Get days from today until target date (KSA timezone)."""
    return (target - today_ksa()).days


def format_date_sa(d: date) -> str:
    """Format date in YYYY-MM-DD (ISO)."""
    return d.isoformat()


def payroll_period_now() -> str:
    """Get current payroll period in YYYY-MM format."""
    return today_ksa().strftime("%Y-%m")


def next_payroll_period() -> str:
    """Get next month's payroll period."""
    t = today_ksa()
    month = t.month + 1
    year = t.year
    if month > 12:
        month = 1
        year += 1
    return f"{year}-{month:02d}"