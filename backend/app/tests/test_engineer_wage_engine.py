"""
Comprehensive deterministic unit tests for the Saudi Engineer Wage Floor Engine.

Tests cover:
- Engineer meeting floor (SSCO 2141xx, salary >= 7000)
- Engineer below floor
- Non-engineer not applicable
- All engineering SSCO prefixes (2141-2149)
"""

from decimal import Decimal

import pytest

from app.engines.engineer_wage_engine import check_engineer_wage_floor


class TestEngineerWageFloor:
    def test_engineer_meets_floor(self):
        """Saudi engineer with SSCO 2141xx and salary >= 7000 passes."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="214101",
            basic_salary=Decimal("7000.00"),
        )
        assert result["is_engineer"] is True
        assert result["meets_floor"] is True
        assert result["wage_floor_applied"] == "engineer_7000"
        assert result["flags"] == []

    def test_engineer_meets_floor_above(self):
        """Saudi engineer with salary well above 7000 passes."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="214101",
            basic_salary=Decimal("15000.00"),
        )
        assert result["is_engineer"] is True
        assert result["meets_floor"] is True
        assert result["flags"] == []

    def test_engineer_below_floor(self):
        """Saudi engineer with salary < 7000 fails."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="214101",
            basic_salary=Decimal("6999.99"),
        )
        assert result["is_engineer"] is True
        assert result["meets_floor"] is False
        assert result["wage_floor_applied"] == "engineer_7000"
        assert "ENGINEER_WAGE_FLOOR_VIOLATION" in result["flags"]

    def test_engineer_below_floor_significantly(self):
        """Saudi engineer with salary significantly below 7000 fails."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="214101",
            basic_salary=Decimal("4000.00"),
        )
        assert result["is_engineer"] is True
        assert result["meets_floor"] is False
        assert "ENGINEER_WAGE_FLOOR_VIOLATION" in result["flags"]

    def test_non_engineer_not_applicable(self):
        """Non-engineer SSCO code → not applicable, passes."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="111101",
            basic_salary=Decimal("5000.00"),
        )
        assert result["is_engineer"] is False
        assert result["meets_floor"] is True  # Not applicable
        assert result["wage_floor_applied"] == "general_4000"
        assert result["flags"] == []

    def test_no_ssco_not_applicable(self):
        """No SSCO code → not applicable, passes."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code=None,
            basic_salary=Decimal("5000.00"),
        )
        assert result["is_engineer"] is False
        assert result["meets_floor"] is True
        assert result["wage_floor_applied"] == "general_4000"
        assert result["flags"] == []

    def test_expat_engineer_not_applicable(self):
        """Expat with engineer SSCO → still detected as engineer but check applies."""
        result = check_engineer_wage_floor(
            nationality="Egyptian",
            ssco_code="214101",
            basic_salary=Decimal("5000.00"),
        )
        # The engine checks SSCO prefix regardless of nationality
        assert result["is_engineer"] is True
        assert result["meets_floor"] is False

    def test_engineer_ssco_prefixes(self):
        """All engineering SSCO prefixes (2141-2146, 2149) are recognized."""
        prefixes = ["2141", "2142", "2143", "2144", "2145", "2146", "2149"]
        for prefix in prefixes:
            result = check_engineer_wage_floor(
                nationality="Saudi",
                ssco_code=f"{prefix}01",
                basic_salary=Decimal("8000.00"),
            )
            assert result["is_engineer"] is True, f"Prefix {prefix} should be engineer"
            assert result["meets_floor"] is True

    def test_non_engineer_ssco_prefixes(self):
        """Non-engineering SSCO prefixes are not flagged as engineers."""
        non_engineer_codes = ["1111", "2111", "2131", "2151", "3111", "4111"]
        for code in non_engineer_codes:
            result = check_engineer_wage_floor(
                nationality="Saudi",
                ssco_code=f"{code}01",
                basic_salary=Decimal("8000.00"),
            )
            assert result["is_engineer"] is False, f"Code {code} should not be engineer"

    def test_engineer_min_salary_value(self):
        """Engineer minimum salary is SAR 7000."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="214101",
            basic_salary=Decimal("7000.00"),
        )
        assert result["engineer_min_salary"] == Decimal("7000.00")

    def test_engineer_exactly_at_floor(self):
        """Engineer at exactly 7000 meets floor."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="214201",
            basic_salary=Decimal("7000.00"),
        )
        assert result["meets_floor"] is True
        assert result["flags"] == []

    def test_engineer_one_below_floor(self):
        """Engineer at 6999.99 fails floor."""
        result = check_engineer_wage_floor(
            nationality="Saudi",
            ssco_code="214301",
            basic_salary=Decimal("6999.99"),
        )
        assert result["meets_floor"] is False
        assert "ENGINEER_WAGE_FLOOR_VIOLATION" in result["flags"]
