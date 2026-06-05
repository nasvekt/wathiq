"""
Comprehensive deterministic unit tests for the GOSI Calculation Engine.

Tests cover:
- Wage base calculation (basic + housing, capped at 45000)
- Scheme classification (legacy vs progressive vs expat)
- Progressive rate step-ups (May 2026, July 2026, ceiling)
- Contribution splits (legacy, progressive, expat)
- Full end-to-end GOSI calculations
"""

from datetime import date
from decimal import Decimal

import pytest

from app.engines.gosi_engine import (
    calculate_gosi_contribution,
    calculate_gosi_wage_base,
    calculate_progressive_rate,
    classify_gosi_scheme,
)


# ── Wage Base Calculation ──────────────────────────────────────────────


class TestGOSIWageBase:
    def test_gosi_wage_base_calculation(self):
        """Basic + housing summed when under cap."""
        result = calculate_gosi_wage_base(
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("2500.00"),
        )
        assert result == Decimal("12500.00")

    def test_gosi_wage_base_cap(self):
        """Wage base capped at SAR 45,000."""
        result = calculate_gosi_wage_base(
            basic_salary=Decimal("40000.00"),
            housing_allowance=Decimal("10000.00"),
        )
        assert result == Decimal("45000.00")

    def test_gosi_wage_base_exactly_at_cap(self):
        """Wage base exactly at cap is not reduced."""
        result = calculate_gosi_wage_base(
            basic_salary=Decimal("30000.00"),
            housing_allowance=Decimal("15000.00"),
        )
        assert result == Decimal("45000.00")

    def test_gosi_wage_base_no_housing(self):
        """Wage base with zero housing equals basic salary."""
        result = calculate_gosi_wage_base(
            basic_salary=Decimal("8000.00"),
            housing_allowance=Decimal("0.00"),
        )
        assert result == Decimal("8000.00")


# ── Scheme Classification ──────────────────────────────────────────────


class TestGOSISchemeClassification:
    def test_classify_gosi_scheme_legacy_by_age(self):
        """Employee aged 50+ at July 2024 transition → legacy."""
        # Born July 1, 1974 → exactly 50 at transition
        result = classify_gosi_scheme(
            nationality="Saudi",
            date_of_birth=date(1974, 7, 1),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result == "legacy"

    def test_classify_gosi_scheme_legacy_by_age_older(self):
        """Employee aged 55 at July 2024 transition → legacy."""
        result = classify_gosi_scheme(
            nationality="Saudi",
            date_of_birth=date(1969, 1, 15),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result == "legacy"

    def test_classify_gosi_scheme_legacy_by_enrollment(self):
        """Employee enrolled 12+ months before July 2024 → legacy."""
        result = classify_gosi_scheme(
            nationality="Saudi",
            date_of_birth=date(1990, 1, 1),
            gosi_enrollment_date=date(2023, 6, 30),  # 12 months + 1 day before
            reference_date=date(2026, 5, 1),
        )
        assert result == "legacy"

    def test_classify_gosi_scheme_legacy_by_enrollment_exact(self):
        """Employee enrolled exactly 12 months before transition → legacy."""
        result = classify_gosi_scheme(
            nationality="Saudi",
            date_of_birth=date(1990, 1, 1),
            gosi_enrollment_date=date(2023, 7, 1),  # exactly 12 months before
            reference_date=date(2026, 5, 1),
        )
        assert result == "legacy"

    def test_classify_gosi_scheme_progressive(self):
        """Under 50, <12 months enrollment → progressive."""
        result = classify_gosi_scheme(
            nationality="Saudi",
            date_of_birth=date(1995, 1, 1),
            gosi_enrollment_date=date(2024, 1, 1),  # only 6 months before
            reference_date=date(2026, 5, 1),
        )
        assert result == "progressive"

    def test_classify_gosi_scheme_progressive_no_dates(self):
        """Saudi with no DOB or enrollment → progressive."""
        result = classify_gosi_scheme(
            nationality="Saudi",
            date_of_birth=None,
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result == "progressive"

    def test_classify_gosi_scheme_expat(self):
        """Non-Saudi → expat."""
        result = classify_gosi_scheme(
            nationality="Egyptian",
            date_of_birth=date(1990, 1, 1),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result == "expat"

    def test_classify_gosi_scheme_expat_case_insensitive(self):
        """Nationality check is case-insensitive for Saudi."""
        result = classify_gosi_scheme(
            nationality="SAUDI ARABIA",
            date_of_birth=date(1995, 1, 1),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result == "progressive"

    def test_classify_gosi_scheme_expat_sa_prefix(self):
        """'SA' prefix is treated as Saudi."""
        result = classify_gosi_scheme(
            nationality="SA",
            date_of_birth=date(1995, 1, 1),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result == "progressive"


# ── Progressive Rate ───────────────────────────────────────────────────


class TestGOSIProgressiveRate:
    def test_progressive_rate_may_2026(self):
        """May 2026: base 22.0% + 2 steps of 0.5% = 23.0%."""
        result = calculate_progressive_rate(reference_date=date(2026, 5, 15))
        assert result == Decimal("0.23")

    def test_progressive_rate_july_2026(self):
        """July 2026: base 22.0% + 3 steps of 0.5% = 23.5%."""
        result = calculate_progressive_rate(reference_date=date(2026, 7, 1))
        assert result == Decimal("0.235")

    def test_progressive_rate_ceiling(self):
        """Rate never exceeds 24.5% cap even after many years."""
        result = calculate_progressive_rate(reference_date=date(2030, 7, 1))
        assert result <= Decimal("0.245")

    def test_progressive_rate_ceiling_far_future(self):
        """Rate capped at 24.5% even in far future."""
        result = calculate_progressive_rate(reference_date=date(2050, 1, 1))
        assert result == Decimal("0.245")

    def test_progressive_rate_at_transition(self):
        """At transition date (July 2024): 0 full years elapsed → base rate 22.0%."""
        result = calculate_progressive_rate(reference_date=date(2024, 7, 1))
        assert result == Decimal("0.22")

    def test_progressive_rate_just_before_second_step(self):
        """June 30, 2026: only 1 full year elapsed → 22.5%."""
        result = calculate_progressive_rate(reference_date=date(2026, 6, 30))
        assert result == Decimal("0.225")


# ── Legacy Contribution Split ──────────────────────────────────────────


class TestGOSILegacySplit:
    def test_legacy_contribution_split(self):
        """Legacy: employer 12%, employee 9.5% of wage base."""
        result = calculate_gosi_contribution(
            nationality="Saudi",
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("2500.00"),
            date_of_birth=date(1970, 1, 1),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result["gosi_scheme"] == "legacy"
        # Employer: 12500 * 0.12 = 1500.00
        assert result["employer_contribution"] == Decimal("1500.00")
        # Employee: 12500 * 0.095 = 1187.50
        assert result["employee_deduction"] == Decimal("1187.50")

    def test_legacy_rate_applied(self):
        """Legacy rate is 21.5%."""
        result = calculate_gosi_contribution(
            nationality="Saudi",
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("0.00"),
            date_of_birth=date(1970, 1, 1),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 1),
        )
        assert result["gosi_rate"] == Decimal("0.215")
        # Total: 10000 * 0.215 = 2150.00
        assert result["total_contribution"] == Decimal("2150.00")


# ── Expat Occupational Hazard ──────────────────────────────────────────


class TestGOSIExpat:
    def test_expat_occupational_hazard(self):
        """Expat: 2% employer-only occupational hazard."""
        result = calculate_gosi_contribution(
            nationality="Egyptian",
            basic_salary=Decimal("5000.00"),
            housing_allowance=Decimal("1000.00"),
            reference_date=date(2026, 5, 1),
        )
        assert result["gosi_scheme"] == "expat"
        assert result["gosi_rate"] == Decimal("0.02")
        # Total: 6000 * 0.02 = 120.00
        assert result["total_contribution"] == Decimal("120.00")
        assert result["employer_contribution"] == Decimal("120.00")
        assert result["employee_deduction"] == Decimal("0.00")


# ── Full GOSI Calculation ──────────────────────────────────────────────


class TestGOSIFullCalculation:
    def test_full_gosi_calculation_saudi_progressive(self):
        """Full progressive Saudi GOSI calculation."""
        result = calculate_gosi_contribution(
            nationality="Saudi",
            basic_salary=Decimal("15000.00"),
            housing_allowance=Decimal("3750.00"),
            date_of_birth=date(1990, 1, 1),
            gosi_enrollment_date=date(2024, 1, 1),
            reference_date=date(2026, 5, 15),
        )
        assert result["gosi_wage_base"] == Decimal("18750.00")
        assert result["gosi_scheme"] == "progressive"
        assert result["gosi_rate"] == Decimal("0.23")
        # Total: 18750 * 0.23 = 4312.50
        assert result["total_contribution"] == Decimal("4312.50")
        # Employer: 18750 * (0.12 + 0.01 SANED) = 2437.50
        assert result["employer_contribution"] == Decimal("2437.50")
        # Employee: 18750 * 0.095 = 1781.25
        assert result["employee_deduction"] == Decimal("1781.25")

    def test_full_gosi_calculation_saudi_legacy(self):
        """Full legacy Saudi GOSI calculation."""
        result = calculate_gosi_contribution(
            nationality="Saudi",
            basic_salary=Decimal("20000.00"),
            housing_allowance=Decimal("5000.00"),
            date_of_birth=date(1970, 1, 1),
            gosi_enrollment_date=None,
            reference_date=date(2026, 5, 15),
        )
        assert result["gosi_wage_base"] == Decimal("25000.00")
        assert result["gosi_scheme"] == "legacy"
        assert result["gosi_rate"] == Decimal("0.215")
        # Total: 25000 * 0.215 = 5375.00
        assert result["total_contribution"] == Decimal("5375.00")
        # Employer: 25000 * 0.12 = 3000.00
        assert result["employer_contribution"] == Decimal("3000.00")
        # Employee: 25000 * 0.095 = 2375.00
        assert result["employee_deduction"] == Decimal("2375.00")

    def test_full_gosi_calculation_expat(self):
        """Full expat GOSI calculation (occupational hazard only)."""
        result = calculate_gosi_contribution(
            nationality="Pakistani",
            basic_salary=Decimal("8000.00"),
            housing_allowance=Decimal("2000.00"),
            reference_date=date(2026, 5, 15),
        )
        assert result["gosi_wage_base"] == Decimal("10000.00")
        assert result["gosi_scheme"] == "expat"
        assert result["gosi_rate"] == Decimal("0.02")
        # Total: 10000 * 0.02 = 200.00
        assert result["total_contribution"] == Decimal("200.00")
        assert result["employer_contribution"] == Decimal("200.00")
        assert result["employee_deduction"] == Decimal("0.00")

    def test_full_gosi_calculation_capped_wage_base(self):
        """GOSI wage base capped at 45000 for high earners."""
        result = calculate_gosi_contribution(
            nationality="Saudi",
            basic_salary=Decimal("40000.00"),
            housing_allowance=Decimal("10000.00"),
            date_of_birth=date(1990, 1, 1),
            gosi_enrollment_date=date(2024, 1, 1),
            reference_date=date(2026, 5, 15),
        )
        # Wage base capped at 45000
        assert result["gosi_wage_base"] == Decimal("45000.00")
        # Total: 45000 * 0.23 = 10350.00
        assert result["total_contribution"] == Decimal("10350.00")
