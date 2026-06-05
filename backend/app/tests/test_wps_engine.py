"""
Comprehensive deterministic unit tests for the WPS (Wage Protection System) Engine.

Tests cover:
- Expatriate minimum wage floor (SAR 3,200)
- Saudi minimum wage check (SAR 4,000)
- Salary variance tolerance (±10%)
"""

from decimal import Decimal

import pytest

from app.engines.wps_engine import check_wps_floor, check_wps_variance


# ── WPS Floor ──────────────────────────────────────────────────────────


class TestWPSFloor:
    def test_wps_floor_expat_pass(self):
        """Expat with gross >= 3200 passes WPS floor."""
        result = check_wps_floor(
            nationality="Egyptian",
            total_gross_wage=Decimal("3200.00"),
        )
        assert result["passed"] is True
        assert result["floor"] == Decimal("3200.00")
        assert result["actual"] == Decimal("3200.00")
        assert result["shortfall"] == Decimal("0.00")

    def test_wps_floor_expat_pass_above(self):
        """Expat with gross well above 3200 passes."""
        result = check_wps_floor(
            nationality="Pakistani",
            total_gross_wage=Decimal("8000.00"),
        )
        assert result["passed"] is True
        assert result["shortfall"] == Decimal("0.00")

    def test_wps_floor_expat_fail(self):
        """Expat with gross < 3200 fails WPS floor."""
        result = check_wps_floor(
            nationality="Indian",
            total_gross_wage=Decimal("3199.99"),
        )
        assert result["passed"] is False
        assert result["floor"] == Decimal("3200.00")
        assert result["shortfall"] == Decimal("0.01")

    def test_wps_floor_expat_fail_low(self):
        """Expat with very low gross fails WPS floor."""
        result = check_wps_floor(
            nationality="Bangladeshi",
            total_gross_wage=Decimal("1500.00"),
        )
        assert result["passed"] is False
        assert result["shortfall"] == Decimal("1700.00")

    def test_wps_floor_saudi_pass(self):
        """Saudi with gross >= 4000 passes."""
        result = check_wps_floor(
            nationality="Saudi",
            total_gross_wage=Decimal("4000.00"),
        )
        assert result["passed"] is True
        assert result["floor"] == Decimal("4000.00")
        assert result["shortfall"] == Decimal("0.00")

    def test_wps_floor_saudi_pass_above(self):
        """Saudi with gross well above 4000 passes."""
        result = check_wps_floor(
            nationality="Saudi",
            total_gross_wage=Decimal("12000.00"),
        )
        assert result["passed"] is True

    def test_wps_floor_saudi_fail(self):
        """Saudi with gross < 4000 fails."""
        result = check_wps_floor(
            nationality="Saudi",
            total_gross_wage=Decimal("3999.99"),
        )
        assert result["passed"] is False
        assert result["floor"] == Decimal("4000.00")
        assert result["shortfall"] == Decimal("0.01")


# ── WPS Variance ───────────────────────────────────────────────────────


class TestWPSVariance:
    def test_wps_variance_within_tolerance(self):
        """Paid within ±10% of registered salary passes."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("10500.00"),
            registered_gosi_contract_salary=Decimal("10000.00"),
        )
        assert result["passed"] is True
        assert result["variance_pct"] == Decimal("5.00")
        assert result["tolerance_pct"] == Decimal("10.00")

    def test_wps_variance_within_tolerance_negative(self):
        """Paid below but within 10% passes."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("9500.00"),
            registered_gosi_contract_salary=Decimal("10000.00"),
        )
        assert result["passed"] is True
        assert result["variance_pct"] == Decimal("5.00")

    def test_wps_variance_exactly_at_tolerance(self):
        """Paid exactly 10% above registered passes (variance == tolerance)."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("11000.00"),
            registered_gosi_contract_salary=Decimal("10000.00"),
        )
        assert result["passed"] is True
        assert result["variance_pct"] == Decimal("10.00")

    def test_wps_variance_exceeds_tolerance(self):
        """Paid more than 10% above registered fails."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("11500.00"),
            registered_gosi_contract_salary=Decimal("10000.00"),
        )
        assert result["passed"] is False
        assert result["variance_pct"] == Decimal("15.00")

    def test_wps_variance_exceeds_tolerance_below(self):
        """Paid more than 10% below registered fails."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("8500.00"),
            registered_gosi_contract_salary=Decimal("10000.00"),
        )
        assert result["passed"] is False
        assert result["variance_pct"] == Decimal("15.00")

    def test_wps_variance_zero_registered_salary(self):
        """Zero registered salary returns failed with message."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("5000.00"),
            registered_gosi_contract_salary=Decimal("0.00"),
        )
        assert result["passed"] is False
        assert result["variance_pct"] == Decimal("0.00")
        assert "zero" in result["message"].lower()

    def test_wps_variance_exact_match(self):
        """Exact match → 0% variance, passes."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("10000.00"),
            registered_gosi_contract_salary=Decimal("10000.00"),
        )
        assert result["passed"] is True
        assert result["variance_pct"] == Decimal("0.00")

    def test_wps_variance_just_over_tolerance(self):
        """Just over 10% fails."""
        result = check_wps_variance(
            paid_gross_wage=Decimal("11001.00"),
            registered_gosi_contract_salary=Decimal("10000.00"),
        )
        assert result["passed"] is False
        assert result["variance_pct"] == Decimal("10.01")
