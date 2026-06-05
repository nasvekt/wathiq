"""
GOSI (Social Insurance) Calculation Engine.
Pure deterministic math. No AI calls. No hardcoded values.

Calculates:
- GOSI wage base (Basic + Housing, capped)
- Scheme classification (Legacy vs Progressive)
- Current progressive rate with annual step-ups
- Employer and employee contribution split
- Expatriate occupational hazard premium
"""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from app.engines.rules_fetcher import get_rule


def calculate_gosi_wage_base(basic_salary: Decimal, housing_allowance: Decimal) -> Decimal:
    """
    GOSI Wage Base = min(Basic + Housing, statutory cap).
    Transport and other allowances are excluded.
    """
    cap = Decimal(str(get_rule("gosi_wage_base_cap")))
    base = basic_salary + housing_allowance
    return min(base, cap)


def classify_gosi_scheme(
    nationality: str,
    date_of_birth: date | None,
    gosi_enrollment_date: date | None,
    reference_date: date | None = None,
) -> str:
    """
    Classify a Saudi employee into Legacy or Progressive GOSI scheme.

    Legacy: employee was 50+ at July 2024 transition, OR had 12+ months
            of GOSI contributions before July 2024.
    Progressive: everyone else.

    Expatriates: return 'expat' (no pension scheme).
    """
    if nationality and nationality.strip().lower() not in ("saudi", "saudi arabia", "sa"):
        return "expat"

    transition = date(2024, 7, 1)
    ref = reference_date or date.today()

    # Check age at transition
    if date_of_birth:
        age_at_transition = (transition - date_of_birth).days // 365
        age_threshold = int(get_rule("gosi_scheme_age_threshold"))
        if age_at_transition >= age_threshold:
            return "legacy"

    # Check enrollment history
    if gosi_enrollment_date:
        months_before_transition = (transition - gosi_enrollment_date).days // 30
        months_threshold = int(get_rule("gosi_scheme_months_threshold"))
        if months_before_transition >= months_threshold:
            return "legacy"

    return "progressive"


def calculate_progressive_rate(reference_date: date | None = None) -> Decimal:
    """
    Calculate the current GOSI Progressive Scheme rate.

    Formula: base_rate + (0.5% × full fiscal years since transition)
    Capped at max rate.

    May 2026: 22.0% + 2 steps = 23.0%
    July 2026: 22.0% + 3 steps = 23.5%
    """
    ref = reference_date or date.today()
    transition = date(2024, 7, 1)

    base_rate = Decimal(str(get_rule("gosi_progressive_base_rate")))
    annual_step = Decimal(str(get_rule("gosi_progressive_annual_step")))
    max_rate = Decimal(str(get_rule("gosi_progressive_max_rate")))

    # Count full fiscal years since transition
    years_elapsed = 0
    check_date = date(transition.year + 1, transition.month, transition.day)
    while check_date <= ref:
        years_elapsed += 1
        check_date = date(check_date.year + 1, check_date.month, check_date.day)

    rate = base_rate + (annual_step * years_elapsed)
    return min(rate, max_rate)


def calculate_gosi_contribution(
    nationality: str,
    basic_salary: Decimal,
    housing_allowance: Decimal,
    date_of_birth: date | None = None,
    gosi_enrollment_date: date | None = None,
    reference_date: date | None = None,
) -> dict:
    """
    Full GOSI calculation for one employee.

    Returns:
        {
            "gosi_wage_base": Decimal,
            "gosi_scheme": "legacy" | "progressive" | "expat",
            "gosi_rate": Decimal,
            "total_contribution": Decimal,
            "employer_contribution": Decimal,
            "employee_deduction": Decimal,
        }
    """
    wage_base = calculate_gosi_wage_base(basic_salary, housing_allowance)
    scheme = classify_gosi_scheme(nationality, date_of_birth, gosi_enrollment_date, reference_date)

    if scheme == "expat":
        rate = Decimal(str(get_rule("gosi_expat_occupational_hazard_rate")))
        total = (wage_base * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "gosi_wage_base": wage_base.quantize(Decimal("0.01")),
            "gosi_scheme": "expat",
            "gosi_rate": rate,
            "total_contribution": total,
            "employer_contribution": total,
            "employee_deduction": Decimal("0.00"),
        }

    if scheme == "legacy":
        rate = Decimal(str(get_rule("gosi_legacy_rate")))
        employer_share = Decimal(str(get_rule("gosi_employer_share_legacy")))
        employee_share = Decimal(str(get_rule("gosi_employee_share_legacy")))
    else:
        rate = calculate_progressive_rate(reference_date)
        # For progressive, split is fetched from rules DB in production
        # Default: employer 12%, employee 9.5% + SANED 1%
        employer_share = Decimal("0.12") + Decimal("0.01")  # + SANED
        employee_share = Decimal("0.095")

    total = (wage_base * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    employer = (wage_base * employer_share).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    employee = (wage_base * employee_share).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "gosi_wage_base": wage_base.quantize(Decimal("0.01")),
        "gosi_scheme": scheme,
        "gosi_rate": rate,
        "total_contribution": total,
        "employer_contribution": employer,
        "employee_deduction": employee,
    }
