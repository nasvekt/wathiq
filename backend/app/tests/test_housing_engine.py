"""
Comprehensive deterministic unit tests for the Housing Allowance Engine.

Tests cover:
- Zero housing allowance flag
- Below recommended minimum (10% of basic)
- Meets minimum threshold
- Exactly at 10% boundary
"""

from decimal import Decimal

import pytest

from app.engines.housing_engine import check_housing_allowance


class TestHousingAllowance:
    def test_housing_zero_flag(self):
        """Zero housing allowance → HOUSING_ZERO flag, not passed."""
        result = check_housing_allowance(
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("0.00"),
        )
        assert result["passed"] is False
        assert "HOUSING_ZERO" in result["flags"]
        assert result["housing_allowance"] == Decimal("0.00")
        assert result["recommended_minimum"] == Decimal("1000.00")
        assert result["actual_pct_of_basic"] == Decimal("0.00")

    def test_housing_below_recommended(self):
        """Housing below 10% of basic → HOUSING_BELOW_RECOMMENDED flag."""
        result = check_housing_allowance(
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("500.00"),
        )
        assert result["passed"] is True  # Has housing, just below recommended
        assert "HOUSING_BELOW_RECOMMENDED" in result["flags"]
        assert "HOUSING_ZERO" not in result["flags"]
        assert result["actual_pct_of_basic"] == Decimal("5.00")

    def test_housing_meets_minimum(self):
        """Housing at 15% of basic → passes, no flags."""
        result = check_housing_allowance(
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("1500.00"),
        )
        assert result["passed"] is True
        assert result["flags"] == []
        assert result["actual_pct_of_basic"] == Decimal("15.00")

    def test_housing_exactly_10_pct(self):
        """Housing at exactly 10% of basic → meets minimum, no flags."""
        result = check_housing_allowance(
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("1000.00"),
        )
        assert result["passed"] is True
        assert result["flags"] == []
        assert result["actual_pct_of_basic"] == Decimal("10.00")
        assert result["recommended_minimum"] == Decimal("1000.00")

    def test_housing_just_below_10_pct(self):
        """Housing at 9.99% of basic → below recommended."""
        result = check_housing_allowance(
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("999.99"),
        )
        assert result["passed"] is True
        assert "HOUSING_BELOW_RECOMMENDED" in result["flags"]

    def test_housing_just_above_10_pct(self):
        """Housing at 10.01% of basic → meets minimum."""
        result = check_housing_allowance(
            basic_salary=Decimal("10000.00"),
            housing_allowance=Decimal("1000.01"),
        )
        assert result["passed"] is True
        assert result["flags"] == []

    def test_housing_zero_basic_salary(self):
        """Zero basic salary → pct is 0, but housing > 0 still passes."""
        result = check_housing_allowance(
            basic_salary=Decimal("0.00"),
            housing_allowance=Decimal("500.00"),
        )
        assert result["passed"] is True
        assert result["actual_pct_of_basic"] == Decimal("0.00")

    def test_housing_large_amount(self):
        """Large housing allowance well above minimum."""
        result = check_housing_allowance(
            basic_salary=Decimal("20000.00"),
            housing_allowance=Decimal("5000.00"),
        )
        assert result["passed"] is True
        assert result["flags"] == []
        assert result["actual_pct_of_basic"] == Decimal("25.00")
