"""
Comprehensive deterministic unit tests for the Qiwa Contract Window Engine.

Tests cover:
- Clear (within 25 days)
- Warning (day 25-29)
- Violation (day 30+)
- Published contract
- No hire date
"""

from datetime import date

import pytest

from app.engines.contract_engine import check_contract_window


class TestContractWindow:
    def test_contract_clear(self):
        """Contract within 25 days → clear."""
        result = check_contract_window(
            hire_date=date(2026, 5, 1),
            contract_published=False,
            reference_date=date(2026, 5, 20),
        )
        assert result["has_hire_date"] is True
        assert result["days_elapsed"] == 19
        assert result["status"] == "clear"
        assert result["flags"] == []

    def test_contract_clear_day_one(self):
        """Contract on hire day → clear."""
        result = check_contract_window(
            hire_date=date(2026, 5, 15),
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["days_elapsed"] == 0
        assert result["status"] == "clear"
        assert result["flags"] == []

    def test_contract_clear_day_24(self):
        """Contract on day 24 → still clear."""
        result = check_contract_window(
            hire_date=date(2026, 4, 21),
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["days_elapsed"] == 24
        assert result["status"] == "clear"

    def test_contract_warning(self):
        """Contract on day 25-29 → warning."""
        result = check_contract_window(
            hire_date=date(2026, 4, 20),
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["days_elapsed"] == 25
        assert result["status"] == "warning"
        assert "QIWA_CONTRACT_WINDOW_WARNING" in result["flags"]

    def test_contract_warning_day_29(self):
        """Contract on day 29 → still warning."""
        result = check_contract_window(
            hire_date=date(2026, 4, 16),
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["days_elapsed"] == 29
        assert result["status"] == "warning"
        assert "QIWA_CONTRACT_WINDOW_WARNING" in result["flags"]

    def test_contract_violation(self):
        """Contract on day 30+ → violation."""
        result = check_contract_window(
            hire_date=date(2026, 4, 15),
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["days_elapsed"] == 30
        assert result["status"] == "violation"
        assert "QIWA_CONTRACT_WINDOW_VIOLATION" in result["flags"]

    def test_contract_violation_day_60(self):
        """Contract on day 60 → violation."""
        result = check_contract_window(
            hire_date=date(2026, 3, 16),
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["days_elapsed"] == 60
        assert result["status"] == "violation"
        assert "QIWA_CONTRACT_WINDOW_VIOLATION" in result["flags"]

    def test_contract_published(self):
        """Published contract → always clear regardless of days elapsed."""
        result = check_contract_window(
            hire_date=date(2026, 1, 1),
            contract_published=True,
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "clear"
        assert result["flags"] == []
        assert result["contract_published"] is True

    def test_contract_published_with_date(self):
        """Published contract with published date → clear."""
        result = check_contract_window(
            hire_date=date(2026, 1, 1),
            contract_published=True,
            contract_published_date=date(2026, 1, 15),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "clear"
        assert result["flags"] == []

    def test_contract_no_hire_date(self):
        """No hire date → unknown status."""
        result = check_contract_window(
            hire_date=None,
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["has_hire_date"] is False
        assert result["days_elapsed"] is None
        assert result["status"] == "unknown"
        assert result["flags"] == []

    def test_contract_window_days_value(self):
        """Contract window is 30 days."""
        result = check_contract_window(
            hire_date=date(2026, 5, 1),
            contract_published=False,
            reference_date=date(2026, 5, 15),
        )
        assert result["window_days"] == 30
        assert result["warning_day"] == 25
