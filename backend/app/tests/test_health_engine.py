"""
Comprehensive deterministic unit tests for the Company Health Score Engine.

Tests cover:
- Perfect score (100)
- Blocked records penalty (-20 each)
- Review records penalty (-5 each)
- Yellow band penalty (-10)
- Red band penalty (-25)
- Iqama expiring penalty (-5 each)
- Iqama expired penalty (-10 each)
- Floor at zero
- Penalty exposure calculation
"""

from decimal import Decimal

import pytest

from app.engines.penalty_engine import calculate_health_score, calculate_penalty_exposure


# ── Health Score ───────────────────────────────────────────────────────


class TestHealthScore:
    def test_perfect_score(self):
        """No issues → score 100, green."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=False,
            red_band=False,
            iqama_expiring_30_days=0,
            iqama_expired=0,
        )
        assert result["score"] == 100
        assert result["color"] == "green"
        assert result["max_score"] == 100

    def test_score_with_blocked(self):
        """Each blocked record deducts 20 points."""
        result = calculate_health_score(
            blocked_count=2,
            review_count=0,
            yellow_band=False,
            red_band=False,
            iqama_expiring_30_days=0,
            iqama_expired=0,
        )
        assert result["score"] == 60
        assert result["deductions"]["blocked_records"] == 40

    def test_score_with_review(self):
        """Each review record deducts 5 points."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=4,
            yellow_band=False,
            red_band=False,
            iqama_expiring_30_days=0,
            iqama_expired=0,
        )
        assert result["score"] == 80
        assert result["deductions"]["review_records"] == 20

    def test_score_yellow_band(self):
        """Yellow band deducts 10 points."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=True,
            red_band=False,
            iqama_expiring_30_days=0,
            iqama_expired=0,
        )
        assert result["score"] == 90
        assert result["color"] == "green"
        assert result["deductions"]["yellow_band"] == 10

    def test_score_red_band(self):
        """Red band deducts 25 points."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=False,
            red_band=True,
            iqama_expiring_30_days=0,
            iqama_expired=0,
        )
        assert result["score"] == 75
        assert result["color"] == "yellow"
        assert result["deductions"]["red_band"] == 25

    def test_score_iqama_expiring(self):
        """Each Iqama expiring within 30 days deducts 5 points."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=False,
            red_band=False,
            iqama_expiring_30_days=3,
            iqama_expired=0,
        )
        assert result["score"] == 85
        assert result["deductions"]["iqama_expiring_30d"] == 15

    def test_score_iqama_expired(self):
        """Each expired Iqama deducts 10 points."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=False,
            red_band=False,
            iqama_expiring_30_days=0,
            iqama_expired=2,
        )
        assert result["score"] == 80
        assert result["deductions"]["iqama_expired"] == 20

    def test_score_floor_at_zero(self):
        """Score never goes below 0."""
        result = calculate_health_score(
            blocked_count=10,
            review_count=10,
            yellow_band=True,
            red_band=True,
            iqama_expiring_30_days=10,
            iqama_expired=10,
        )
        assert result["score"] == 0
        assert result["color"] == "red"

    def test_score_combined_penalties(self):
        """Multiple penalties combined correctly."""
        result = calculate_health_score(
            blocked_count=1,  # -20
            review_count=2,  # -10
            yellow_band=True,  # -10
            red_band=False,
            iqama_expiring_30_days=1,  # -5
            iqama_expired=1,  # -10
        )
        # 100 - 20 - 10 - 10 - 5 - 10 = 45
        assert result["score"] == 45
        assert result["color"] == "red"

    def test_score_yellow_band_boundary(self):
        """Score exactly 70 → yellow."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=False,
            red_band=True,  # -25
            iqama_expiring_30_days=1,  # -5
            iqama_expired=0,
        )
        # 100 - 25 - 5 = 70
        assert result["score"] == 70
        assert result["color"] == "yellow"

    def test_score_just_below_yellow(self):
        """Score 69 → red."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=False,
            red_band=True,  # -25
            iqama_expiring_30_days=2,  # -10
            iqama_expired=0,
        )
        # 100 - 25 - 10 = 65
        assert result["score"] == 65
        assert result["color"] == "red"

    def test_score_green_boundary(self):
        """Score exactly 90 → green."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=True,  # -10
            red_band=False,
            iqama_expiring_30_days=0,
            iqama_expired=0,
        )
        assert result["score"] == 90
        assert result["color"] == "green"

    def test_score_just_below_green(self):
        """Score 89 → yellow."""
        result = calculate_health_score(
            blocked_count=0,
            review_count=0,
            yellow_band=True,  # -10
            red_band=False,
            iqama_expiring_30_days=1,  # -5
            iqama_expired=0,
        )
        # 100 - 10 - 5 = 85
        assert result["score"] == 85
        assert result["color"] == "yellow"

    def test_deductions_structure(self):
        """All deduction keys present in result."""
        result = calculate_health_score(
            blocked_count=1,
            review_count=1,
            yellow_band=True,
            red_band=True,
            iqama_expiring_30_days=1,
            iqama_expired=1,
        )
        expected_keys = {
            "blocked_records",
            "review_records",
            "yellow_band",
            "red_band",
            "iqama_expiring_30d",
            "iqama_expired",
        }
        assert set(result["deductions"].keys()) == expected_keys


# ── Penalty Exposure ───────────────────────────────────────────────────


class TestPenaltyExposure:
    def test_penalty_exposure_calculation(self):
        """SAR 5,000 per blocked + SAR 1,500 per review."""
        result = calculate_penalty_exposure(
            blocked_count=2,
            review_count=3,
        )
        # 2 * 5000 + 3 * 1500 = 10000 + 4500 = 14500
        assert result == Decimal("14500.00")

    def test_penalty_exposure_zero(self):
        """No blocked or review → zero exposure."""
        result = calculate_penalty_exposure(
            blocked_count=0,
            review_count=0,
        )
        assert result == Decimal("0.00")

    def test_penalty_exposure_blocked_only(self):
        """Only blocked records."""
        result = calculate_penalty_exposure(
            blocked_count=3,
            review_count=0,
        )
        assert result == Decimal("15000.00")

    def test_penalty_exposure_review_only(self):
        """Only review records."""
        result = calculate_penalty_exposure(
            blocked_count=0,
            review_count=4,
        )
        assert result == Decimal("6000.00")

    def test_penalty_exposure_single_blocked(self):
        """Single blocked record → SAR 5,000."""
        result = calculate_penalty_exposure(blocked_count=1, review_count=0)
        assert result == Decimal("5000.00")

    def test_penalty_exposure_single_review(self):
        """Single review record → SAR 1,500."""
        result = calculate_penalty_exposure(blocked_count=0, review_count=1)
        assert result == Decimal("1500.00")

    def test_penalty_exposure_large(self):
        """Large number of violations."""
        result = calculate_penalty_exposure(
            blocked_count=20,
            review_count=50,
        )
        # 20 * 5000 + 50 * 1500 = 100000 + 75000 = 175000
        assert result == Decimal("175000.00")
