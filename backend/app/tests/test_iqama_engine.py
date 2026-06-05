"""
Comprehensive deterministic unit tests for the Iqama Expiry Engine.

Tests cover:
- Expired Iqama
- Expiring within 30 days
- Expiring within 7 days
- Valid (not expiring soon)
- No expiry date
"""

from datetime import date

import pytest

from app.engines.iqama_engine import check_iqama_expiry


class TestIqamaExpiry:
    def test_iqama_expired(self):
        """Iqama already expired → status expired, alert triggered."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 4, 1),
            reference_date=date(2026, 5, 15),
        )
        assert result["has_expiry_date"] is True
        assert result["status"] == "expired"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == "expired"
        assert result["days_remaining"] == -44

    def test_iqama_expired_yesterday(self):
        """Iqama expired yesterday."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 5, 14),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "expired"
        assert result["days_remaining"] == -1

    def test_iqama_expiring_30_days(self):
        """Iqama expiring in exactly 30 days → at_risk, alert at 30."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 6, 14),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "at_risk"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == 30
        assert result["days_remaining"] == 30

    def test_iqama_expiring_7_days(self):
        """Iqama expiring in exactly 7 days → at_risk, alert at 7."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 5, 22),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "at_risk"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == 7
        assert result["days_remaining"] == 7

    def test_iqama_expiring_29_days(self):
        """Iqama expiring in 29 days → alert at 30 (closest crossed threshold)."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 6, 13),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "at_risk"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == 30

    def test_iqama_expiring_6_days(self):
        """Iqama expiring in 6 days → alert at 7."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 5, 21),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "at_risk"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == 7

    def test_iqama_valid(self):
        """Iqama expiring in 90+ days → valid, no alert."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 9, 1),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "valid"
        assert result["alert_triggered"] is False
        assert result["alert_level"] is None

    def test_iqama_valid_60_days(self):
        """Iqama expiring in 60 days → at_risk, alert at 60."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 7, 14),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "at_risk"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == 60

    def test_iqama_valid_89_days(self):
        """Iqama expiring in 89 days → at_risk, alert at 90."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 8, 12),
            reference_date=date(2026, 5, 15),
        )
        assert result["status"] == "at_risk"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == 90

    def test_iqama_no_date(self):
        """No Iqama expiry date → unknown status."""
        result = check_iqama_expiry(
            iqama_expiry_date=None,
            reference_date=date(2026, 5, 15),
        )
        assert result["has_expiry_date"] is False
        assert result["expiry_date"] is None
        assert result["days_remaining"] is None
        assert result["status"] == "unknown"
        assert result["alert_triggered"] is False
        assert result["alert_level"] is None

    def test_iqama_expires_today(self):
        """Iqama expiring today → 0 days remaining, at_risk, alert at 7."""
        result = check_iqama_expiry(
            iqama_expiry_date=date(2026, 5, 15),
            reference_date=date(2026, 5, 15),
        )
        assert result["days_remaining"] == 0
        assert result["status"] == "at_risk"
        assert result["alert_triggered"] is True
        assert result["alert_level"] == 7
