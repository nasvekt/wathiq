"""
Comprehensive deterministic unit tests for the Nitaqat (Saudization) Engine.

Tests cover:
- Individual employee Nitaqat weight calculation
- Saudization ratio computation
- Nitaqat band classification
- Procurement-specific Saudization
"""

from decimal import Decimal

import pytest

from app.engines.nitaqat_engine import (
    calculate_nitaqat_weight,
    calculate_procurement_saudization,
    calculate_saudization_ratio,
    classify_nitaqat_band,
)


# ── Nitaqat Weight ─────────────────────────────────────────────────────


class TestNitaqatWeight:
    def test_nitaqat_weight_full(self):
        """Saudi with gross >= 4000 → weight 1.0."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("4000.00"),
        )
        assert result == Decimal("1.0")

    def test_nitaqat_weight_full_above(self):
        """Saudi with gross well above 4000 → weight 1.0."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("15000.00"),
        )
        assert result == Decimal("1.0")

    def test_nitaqat_weight_half(self):
        """Saudi with gross 3000-3999 → weight 0.5."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("3500.00"),
        )
        assert result == Decimal("0.5")

    def test_nitaqat_weight_half_at_min(self):
        """Saudi with gross exactly 3000 → weight 0.5."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("3000.00"),
        )
        assert result == Decimal("0.5")

    def test_nitaqat_weight_half_at_max(self):
        """Saudi with gross exactly 3999.99 → weight 0.5."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("3999.99"),
        )
        assert result == Decimal("0.5")

    def test_nitaqat_weight_zero(self):
        """Saudi with gross < 3000 → weight 0.0."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("2999.99"),
        )
        assert result == Decimal("0.0")

    def test_nitaqat_weight_zero_minimal(self):
        """Saudi with very low gross → weight 0.0."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("500.00"),
        )
        assert result == Decimal("0.0")

    def test_nitaqat_weight_expat(self):
        """Expatriate always gets weight 0.0 regardless of wage."""
        result = calculate_nitaqat_weight(
            nationality="Egyptian",
            total_gross_wage=Decimal("10000.00"),
        )
        assert result == Decimal("0.0")

    def test_nitaqat_weight_expat_low_wage(self):
        """Expatriate with low wage → weight 0.0."""
        result = calculate_nitaqat_weight(
            nationality="Pakistani",
            total_gross_wage=Decimal("1500.00"),
        )
        assert result == Decimal("0.0")

    def test_nitaqat_weight_part_time(self):
        """Saudi part-time with >= 160 hours → weight 1.0."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("2000.00"),
            monthly_hours=160,
        )
        assert result == Decimal("1.0")

    def test_nitaqat_weight_part_time_above_threshold(self):
        """Saudi part-time with > 160 hours → weight 1.0."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("2000.00"),
            monthly_hours=200,
        )
        assert result == Decimal("1.0")

    def test_nitaqat_weight_part_time_below_threshold(self):
        """Saudi part-time with < 160 hours → falls through to wage check."""
        result = calculate_nitaqat_weight(
            nationality="Saudi",
            total_gross_wage=Decimal("2000.00"),
            monthly_hours=100,
        )
        assert result == Decimal("0.0")

    def test_nitaqat_weight_expat_part_time(self):
        """Expat part-time still gets 0.0 (expat check comes first)."""
        result = calculate_nitaqat_weight(
            nationality="Indian",
            total_gross_wage=Decimal("5000.00"),
            monthly_hours=200,
        )
        assert result == Decimal("0.0")


# ── Saudization Ratio ──────────────────────────────────────────────────


class TestSaudizationRatio:
    def test_saudization_ratio_calculation(self):
        """3 Saudis at full weight out of 10 total → 30.0%."""
        result = calculate_saudization_ratio(
            total_employees=10,
            saudi_weights_sum=Decimal("3.0"),
        )
        assert result == Decimal("30.00")

    def test_saudization_ratio_zero_employees(self):
        """Zero total employees → 0.0%."""
        result = calculate_saudization_ratio(
            total_employees=0,
            saudi_weights_sum=Decimal("0.0"),
        )
        assert result == Decimal("0.0")

    def test_saudization_ratio_all_saudis(self):
        """All Saudis at full weight → 100.0%."""
        result = calculate_saudization_ratio(
            total_employees=5,
            saudi_weights_sum=Decimal("5.0"),
        )
        assert result == Decimal("100.00")

    def test_saudization_ratio_mixed_weights(self):
        """Mixed weights: 2 full + 1 half out of 5 → 50.0%."""
        result = calculate_saudization_ratio(
            total_employees=5,
            saudi_weights_sum=Decimal("2.5"),
        )
        assert result == Decimal("50.00")

    def test_saudization_ratio_no_saudis(self):
        """No Saudi employees → 0.0%."""
        result = calculate_saudization_ratio(
            total_employees=8,
            saudi_weights_sum=Decimal("0.0"),
        )
        assert result == Decimal("0.00")

    def test_saudization_ratio_single_saudi(self):
        """Single Saudi at full weight out of 1 → 100.0%."""
        result = calculate_saudization_ratio(
            total_employees=1,
            saudi_weights_sum=Decimal("1.0"),
        )
        assert result == Decimal("100.00")


# ── Nitaqat Band Classification ────────────────────────────────────────


class TestNitaqatBand:
    def test_nitaqat_band_technology_medium_a(self):
        """Technology medium_a: platinum >= 40%, high_green >= 35%, etc."""
        # Platinum
        assert classify_nitaqat_band(Decimal("45.0"), "technology", "medium_a") == "platinum"
        # High green
        assert classify_nitaqat_band(Decimal("37.0"), "technology", "medium_a") == "high_green"
        # Low green
        assert classify_nitaqat_band(Decimal("28.0"), "technology", "medium_a") == "low_green"
        # Yellow
        assert classify_nitaqat_band(Decimal("20.0"), "technology", "medium_a") == "yellow"
        # Red
        assert classify_nitaqat_band(Decimal("10.0"), "technology", "medium_a") == "red"

    def test_nitaqat_band_construction_medium_a(self):
        """Construction medium_a: platinum >= 25%, high_green >= 20%, etc."""
        # Platinum
        assert classify_nitaqat_band(Decimal("30.0"), "construction", "medium_a") == "platinum"
        # High green
        assert classify_nitaqat_band(Decimal("22.0"), "construction", "medium_a") == "high_green"
        # Low green
        assert classify_nitaqat_band(Decimal("15.0"), "construction", "medium_a") == "low_green"
        # Yellow
        assert classify_nitaqat_band(Decimal("10.0"), "construction", "medium_a") == "yellow"
        # Red
        assert classify_nitaqat_band(Decimal("5.0"), "construction", "medium_a") == "red"

    def test_nitaqat_band_red(self):
        """Very low Saudization → red band."""
        assert classify_nitaqat_band(Decimal("5.0"), "technology", "medium_a") == "red"
        assert classify_nitaqat_band(Decimal("1.0"), "construction", "medium_a") == "red"

    def test_nitaqat_band_exact_thresholds(self):
        """Test exact boundary values for technology medium_a."""
        assert classify_nitaqat_band(Decimal("40.0"), "technology", "medium_a") == "platinum"
        assert classify_nitaqat_band(Decimal("35.0"), "technology", "medium_a") == "high_green"
        assert classify_nitaqat_band(Decimal("26.0"), "technology", "medium_a") == "low_green"
        assert classify_nitaqat_band(Decimal("18.0"), "technology", "medium_a") == "yellow"
        assert classify_nitaqat_band(Decimal("17.99"), "technology", "medium_a") == "red"

    def test_nitaqat_band_unknown_sector(self):
        """Unknown sector uses default conservative thresholds."""
        result = classify_nitaqat_band(Decimal("30.0"), "unknown_sector", "medium_a")
        # Default: platinum 40, high_green 35, low_green 25, yellow 15
        assert result == "low_green"

    def test_nitaqat_band_unknown_size(self):
        """Unknown size category uses sector defaults."""
        result = classify_nitaqat_band(Decimal("30.0"), "technology", "unknown_size")
        # Falls back to sector data which won't have the size, so empty thresholds → defaults
        assert result == "low_green"


# ── Procurement Saudization ────────────────────────────────────────────


class TestProcurementSaudization:
    def test_procurement_saudization_meets_70_pct(self):
        """Procurement with >= 70% Saudization passes."""
        employees = [
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Egyptian", "total_gross_wage": Decimal("3000.00")},
            {"nationality": "Egyptian", "total_gross_wage": Decimal("3000.00")},
            {"nationality": "Egyptian", "total_gross_wage": Decimal("3000.00")},
        ]
        result = calculate_procurement_saudization(employees)
        assert result["total_procurement_headcount"] == 10
        assert result["saudi_procurement_count"] == 7
        assert result["saudi_procurement_weight_sum"] == Decimal("7.0")
        assert result["procurement_saudization_pct"] == Decimal("70.00")
        assert result["meets_70_pct_rule"] is True

    def test_procurement_saudization_below_70_pct(self):
        """Procurement with < 70% Saudization fails."""
        employees = [
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Saudi", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Egyptian", "total_gross_wage": Decimal("3000.00")},
            {"nationality": "Egyptian", "total_gross_wage": Decimal("3000.00")},
            {"nationality": "Egyptian", "total_gross_wage": Decimal("3000.00")},
            {"nationality": "Egyptian", "total_gross_wage": Decimal("3000.00")},
        ]
        result = calculate_procurement_saudization(employees)
        assert result["total_procurement_headcount"] == 10
        assert result["saudi_procurement_count"] == 6
        assert result["saudi_procurement_weight_sum"] == Decimal("6.0")
        assert result["procurement_saudization_pct"] == Decimal("60.00")
        assert result["meets_70_pct_rule"] is False

    def test_procurement_saudization_empty(self):
        """Empty procurement list returns zeros and passes."""
        result = calculate_procurement_saudization([])
        assert result["total_procurement_headcount"] == 0
        assert result["saudi_procurement_count"] == 0
        assert result["saudi_procurement_weight_sum"] == Decimal("0.00")
        assert result["procurement_saudization_pct"] == Decimal("0.00")
        assert result["meets_70_pct_rule"] is True

    def test_procurement_saudization_all_expat(self):
        """All expat procurement → 0% Saudization."""
        employees = [
            {"nationality": "Egyptian", "total_gross_wage": Decimal("5000.00")},
            {"nationality": "Indian", "total_gross_wage": Decimal("4000.00")},
        ]
        result = calculate_procurement_saudization(employees)
        assert result["saudi_procurement_count"] == 0
        assert result["procurement_saudization_pct"] == Decimal("0.00")
        assert result["meets_70_pct_rule"] is False
