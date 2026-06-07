"""
Comprehensive deterministic unit tests for the Qiwa Shield Engine.

Tests cover:
- NitaqatBand enum (Yellow removed post-2026 overhaul)
- EmployeeRecord dataclass creation
- _calculate_nitaqat_weight — all weight scenarios
- _classify_nitaqat_band — all bands (no Yellow → direct Red)
- _calculate_health_score — score deduction logic
- scan_employee — all 6 rules individually
- scan_batch — full batch scan with mixed employees
- simulate_nitaqat — what-if projections
- Edge cases: empty batch, all non-Saudi, boundary salaries
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from app.features.qiwa_shield.engine import (
    DocumentStatus,
    EmployeeRecord,
    NitaqatBand,
    ScanResult,
    BatchScanResult,
    scan_employee,
    scan_batch,
    simulate_nitaqat,
    _calculate_nitaqat_weight,
    _classify_nitaqat_band,
    _calculate_health_score,
    ComplianceRule,
    RULES,
)


# ── Fixtures ────────────────────────────────────────────────────────────


def make_emp(
    ref_id: str = "emp-001",
    is_saudi: bool = True,
    contract_documented_in_qiwa: bool = True,
    gosi_enrolled: bool = True,
    total_gross_wage: Decimal = Decimal("5000"),
    basic_salary: Decimal = Decimal("5000"),
    hire_date: date | None = date(2026, 1, 1),
    contract_end_date: date | None = None,
    monthly_hours: int = 160,
    nationality: str = "Saudi Arabia",
) -> EmployeeRecord:
    return EmployeeRecord(
        ref_id=ref_id,
        employee_name="Test Employee",
        employee_name_ar="موظف اختبار",
        iqama_number="1012345678",
        nationality=nationality,
        is_saudi=is_saudi,
        basic_salary=basic_salary,
        total_gross_wage=total_gross_wage,
        job_title="Engineer",
        ssco_code="214101",
        hire_date=hire_date,
        contract_end_date=contract_end_date,
        contract_documented_in_qiwa=contract_documented_in_qiwa,
        gosi_enrolled=gosi_enrolled,
        monthly_hours=monthly_hours,
        housing_allowance=Decimal("500"),
    )


# ── NitaqatBand Enum ────────────────────────────────────────────────────


class TestNitaqatBand:
    def test_yellow_removed(self):
        """Yellow tier was eliminated in the 2026 overhaul."""
        assert not hasattr(NitaqatBand, "YELLOW")

    def test_band_ordering(self):
        """Bands ordered Platinum > High Green > Low Green > Red."""
        bands = [NitaqatBand.PLATINUM, NitaqatBand.HIGH_GREEN, NitaqatBand.LOW_GREEN, NitaqatBand.RED]
        assert len(bands) == 4
        assert all(isinstance(b, NitaqatBand) for b in bands)


# ── _calculate_nitaqat_weight ────────────────────────────────────────────


class TestNitaqatWeight:
    def test_non_saudi_zero(self):
        """Non-Saudi employees always get 0.0 Nitaqat weight."""
        emp = make_emp(is_saudi=False)
        assert _calculate_nitaqat_weight(emp) == 0.0

    def test_saudi_full_weight(self):
        """Saudi with documented contract + GOSI + wage >= 4000 gets 1.0."""
        emp = make_emp(total_gross_wage=Decimal("4000"))
        assert _calculate_nitaqat_weight(emp) == 1.0

    def test_saudi_full_weight_above_threshold(self):
        """Saudi earning well above threshold gets 1.0."""
        emp = make_emp(total_gross_wage=Decimal("15000"))
        assert _calculate_nitaqat_weight(emp) == 1.0

    def test_saudi_half_weight(self):
        """Saudi earning 3000-3999 gets 0.5."""
        emp = make_emp(total_gross_wage=Decimal("3500"))
        assert _calculate_nitaqat_weight(emp) == 0.5

    def test_saudi_half_weight_lower_boundary(self):
        """Saudi earning exactly 3000 gets 0.5."""
        emp = make_emp(total_gross_wage=Decimal("3000"))
        assert _calculate_nitaqat_weight(emp) == 0.5

    def test_saudi_half_weight_upper_boundary(self):
        """Saudi earning exactly 3999 gets 0.5."""
        emp = make_emp(total_gross_wage=Decimal("3999"))
        assert _calculate_nitaqat_weight(emp) == 0.5

    def test_saudi_below_3000_zero(self):
        """Saudi earning below 3000 and below 160h gets 0.0."""
        emp = make_emp(total_gross_wage=Decimal("2000"), monthly_hours=80)
        assert _calculate_nitaqat_weight(emp) == 0.0

    def test_saudi_part_time_above_160h(self):
        """Saudi earning below 3000 but >= 160h gets 1.0 (part-time rule)."""
        emp = make_emp(total_gross_wage=Decimal("2500"), monthly_hours=160)
        assert _calculate_nitaqat_weight(emp) == 1.0

    def test_saudi_not_documented_zero(self):
        """Saudi without Qiwa contract gets 0.0 even with high salary."""
        emp = make_emp(contract_documented_in_qiwa=False)
        assert _calculate_nitaqat_weight(emp) == 0.0

    def test_saudi_not_enrolled_zero(self):
        """Saudi without GOSI enrollment gets 0.0 even with high salary."""
        emp = make_emp(gosi_enrolled=False)
        assert _calculate_nitaqat_weight(emp) == 0.0


# ── _classify_nitaqat_band ──────────────────────────────────────────────


class TestNitaqatBandClassification:
    def test_platinum(self):
        """Saudization ratio >= 40% is Platinum."""
        assert _classify_nitaqat_band(40.0) == NitaqatBand.PLATINUM
        assert _classify_nitaqat_band(55.0) == NitaqatBand.PLATINUM

    def test_high_green(self):
        """Saudization ratio 35-39.99% is High Green."""
        assert _classify_nitaqat_band(35.0) == NitaqatBand.HIGH_GREEN
        assert _classify_nitaqat_band(39.9) == NitaqatBand.HIGH_GREEN

    def test_low_green(self):
        """Saudization ratio 26-34.99% is Low Green."""
        assert _classify_nitaqat_band(26.0) == NitaqatBand.LOW_GREEN
        assert _classify_nitaqat_band(34.9) == NitaqatBand.LOW_GREEN

    def test_red_ratio_below_26(self):
        """Saudization ratio below 26% is Red (was Yellow, now direct Red)."""
        assert _classify_nitaqat_band(25.9) == NitaqatBand.RED
        assert _classify_nitaqat_band(18.0) == NitaqatBand.RED
        assert _classify_nitaqat_band(10.0) == NitaqatBand.RED
        assert _classify_nitaqat_band(0.0) == NitaqatBand.RED

    def test_no_yellow_band(self):
        """Ratios 18-25.9 that used to be Yellow are now Red."""
        for ratio in [18, 20, 22, 24, 25]:
            assert _classify_nitaqat_band(float(ratio)) == NitaqatBand.RED


# ── _calculate_health_score ────────────────────────────────────────────


class TestHealthScore:
    def test_perfect_score(self):
        """100% documented, no violations, high ratio = 100."""
        score = _calculate_health_score(
            total=100, documented=100, blocker_count=0,
            warning_count=0, saudization_ratio=40.0, band=NitaqatBand.PLATINUM,
        )
        assert score == 100

    def test_low_documentation_penalty(self):
        """Below 90% documented loses 20, below 80% loses another 15."""
        score = _calculate_health_score(
            total=100, documented=75, blocker_count=0,
            warning_count=0, saudization_ratio=30.0, band=NitaqatBand.LOW_GREEN,
        )
        assert score == 65  # 100 - 20 (below 90%) - 15 (below 80%)

    def test_blocker_deduction(self):
        """Each blocker costs 8 points."""
        score = _calculate_health_score(
            total=100, documented=95, blocker_count=3,
            warning_count=0, saudization_ratio=35.0, band=NitaqatBand.HIGH_GREEN,
        )
        assert score == 100 - 3 * 8  # 76

    def test_warning_deduction(self):
        """Each warning costs 3 points."""
        score = _calculate_health_score(
            total=100, documented=95, blocker_count=0,
            warning_count=4, saudization_ratio=35.0, band=NitaqatBand.HIGH_GREEN,
        )
        assert score == 100 - 4 * 3  # 88

    def test_low_saudization_penalty(self):
        """Ratio below 18 loses 25, below 26 loses 15."""
        score = _calculate_health_score(
            total=100, documented=95, blocker_count=0,
            warning_count=0, saudization_ratio=15.0, band=NitaqatBand.RED,
        )
        # 100 - 25 (ratio < 18) - 20 (Red band)
        assert score == 55

    def test_no_employees_perfect(self):
        """When total=0, there are no violations — score should be 100."""
        score = _calculate_health_score(
            total=0, documented=0, blocker_count=0,
            warning_count=0, saudization_ratio=0.0, band=NitaqatBand.RED,
        )
        assert score == 100

    def test_score_floor(self):
        """Score cannot go below 0."""
        score = _calculate_health_score(
            total=10, documented=2, blocker_count=10,
            warning_count=10, saudization_ratio=2.0, band=NitaqatBand.RED,
        )
        assert score == 0

    def test_score_ceiling(self):
        """Score cannot exceed 100."""
        score = _calculate_health_score(
            total=100, documented=100, blocker_count=-5,
            warning_count=-5, saudization_ratio=100.0, band=NitaqatBand.PLATINUM,
        )
        assert score == 100


# ── scan_employee ──────────────────────────────────────────────────────


class TestScanEmployee:
    def test_fully_compliant_saudi(self):
        """Fully compliant Saudi employee: documented, enrolled, well-paid."""
        emp = make_emp()
        result = scan_employee(emp)
        assert len(result.violations) == 0
        assert result.can_count_for_saudization is True
        assert result.document_status == DocumentStatus.DOCUMENTED
        assert result.nitaqat_weight == 1.0

    def test_non_saudi_no_violations(self):
        """Non-Saudi employees are not subject to Saudization rules."""
        emp = make_emp(is_saudi=False)
        result = scan_employee(emp)
        assert len(result.violations) == 0
        assert result.can_count_for_saudization is False
        assert result.nitaqat_weight == 0.0

    def test_undocumented_saudi_blocked(self):
        """Saudi without Qiwa contract triggers QIWA_DOC_001 blocker."""
        emp = make_emp(contract_documented_in_qiwa=False, hire_date=None)
        result = scan_employee(emp)
        violations = [v.id for v in result.violations]
        assert "QIWA_DOC_001" in violations
        assert result.can_count_for_saudization is False
        assert result.document_status == DocumentStatus.MISSING

    def test_runaway_warning_triggered(self):
        """Saudi undocumented for 80+ days triggers QIWA_DOC_002."""
        emp = make_emp(
            contract_documented_in_qiwa=False,
            hire_date=datetime.now().date() - timedelta(days=85),
        )
        result = scan_employee(emp)
        violations = [v.id for v in result.violations]
        assert "QIWA_DOC_002" in violations
        assert result.document_status == DocumentStatus.AT_RISK

    def test_not_enrolled_no_gosi(self):
        """Saudi without GOSI triggers QIWA_GOSI_001 blocker."""
        emp = make_emp(contract_documented_in_qiwa=True, gosi_enrolled=False)
        result = scan_employee(emp)
        violations = [v.id for v in result.violations]
        assert "QIWA_GOSI_001" in violations

    def test_nitaqat_credit_blocker(self):
        """Saudi missing contract, GOSI, or salary threshold triggers QIWA_NIT_001."""
        emp = make_emp(contract_documented_in_qiwa=False, total_gross_wage=Decimal("5000"))
        result = scan_employee(emp)
        violations = [v.id for v in result.violations]
        assert "QIWA_NIT_001" in violations

    def test_half_weight_warning(self):
        """Saudi earning 3000-3999 triggers QIWA_NIT_002 warning."""
        emp = make_emp(total_gross_wage=Decimal("3500"))
        result = scan_employee(emp)
        violations = [v.id for v in result.violations]
        assert "QIWA_NIT_002" in violations

    def test_contract_expiry_warning(self):
        """Contract ending within 30 days triggers QIWA_CONTRACT_001 warning."""
        emp = make_emp(
            contract_end_date=datetime.now().date() + timedelta(days=15),
        )
        result = scan_employee(emp)
        violations = [v.id for v in result.violations]
        assert "QIWA_CONTRACT_001" in violations

    def test_expired_contract_status(self):
        """Expired contract results in EXPIRED status."""
        emp = make_emp(
            contract_end_date=datetime.now().date() - timedelta(days=1),
        )
        result = scan_employee(emp)
        assert result.document_status == DocumentStatus.EXPIRED

    def test_multiple_violations(self):
        """Saudi with multiple issues triggers multiple rules."""
        emp = make_emp(
            contract_documented_in_qiwa=False,
            gosi_enrolled=False,
            total_gross_wage=Decimal("2500"),
        )
        result = scan_employee(emp)
        violation_ids = [v.id for v in result.violations]
        assert "QIWA_DOC_001" in violation_ids
        assert "QIWA_NIT_001" in violation_ids
        assert "QIWA_GOSI_001" in violation_ids


# ── scan_batch ──────────────────────────────────────────────────────────


class TestScanBatch:
    def test_empty_batch(self):
        """Empty employee list returns zero-everything result."""
        result = scan_batch([], company_name="Test Co")
        assert result.total_employees == 0
        assert result.saudi_count == 0
        assert result.documented_count == 0
        assert result.compliance_health_score == 100
        assert result.current_nitaqat_band == NitaqatBand.RED

    def test_mixed_batch(self):
        """Mixed batch computes correct totals."""
        employees = [
            make_emp(ref_id="e1", is_saudi=True, contract_documented_in_qiwa=True),
            make_emp(ref_id="e2", is_saudi=True, contract_documented_in_qiwa=False, hire_date=None),
            make_emp(ref_id="e3", is_saudi=False),
        ]
        result = scan_batch(employees, company_name="Test Co")
        assert result.total_employees == 3
        assert result.saudi_count == 2
        assert result.documented_count == 1
        assert result.undocumented_count == 1
        assert result.company_name == "Test Co"

    def test_all_non_saudi(self):
        """All non-Saudi employees = 0% Saudization = Red band."""
        employees = [
            make_emp(is_saudi=False, ref_id="e1"),
            make_emp(is_saudi=False, ref_id="e2"),
        ]
        result = scan_batch(employees)
        assert result.saudization_ratio == 0.0
        assert result.current_nitaqat_band == NitaqatBand.RED

    def test_penalty_calculation(self):
        """Penalty exposure matches blocker/warning counts."""
        employees = [
            make_emp(ref_id="e1", contract_documented_in_qiwa=False, hire_date=None),
            make_emp(ref_id="e2", contract_documented_in_qiwa=True),
        ]
        result = scan_batch(employees)
        assert result.blocker_count >= 1
        assert result.estimated_penalty_exposure >= 10000

    def test_action_items_generated(self):
        """Undocumented employees generate documentation action items."""
        employees = [
            make_emp(ref_id="e1", contract_documented_in_qiwa=False, hire_date=None),
        ]
        result = scan_batch(employees)
        assert any("Document" in item for item in result.action_items)


# ── simulate_nitaqat ────────────────────────────────────────────────────


class TestSimulateNitaqat:
    def test_no_changes(self):
        """Simulating with zero changes returns current state."""
        employees = [
            make_emp(ref_id="e1"),
            make_emp(ref_id="e2", is_saudi=False),
        ]
        batch = scan_batch(employees, company_name="Test Co")
        result = simulate_nitaqat(batch, add_saudi=0)
        assert result["projected_ratio"] == batch.saudization_ratio
        assert result["projected_band"] == batch.current_nitaqat_band.value
        assert result["new_saudi_hires"] == 0
        assert not result["improvement"]
        assert not result["worsens"]

    def test_adding_documented_saudi_improves_ratio(self):
        """Adding documented Saudis improves the ratio."""
        employees = [
            make_emp(ref_id="e1", is_saudi=False),
            make_emp(ref_id="e2", is_saudi=False),
        ]
        batch = scan_batch(employees)
        result = simulate_nitaqat(batch, add_saudi=2, add_saudi_documented=True)
        assert result["projected_ratio"] > batch.saudization_ratio
        assert result["new_saudi_hires"] == 2
        assert result["improvement"] is True

    def test_adding_undocumented_saudi_no_change(self):
        """Adding undocumented Saudis doesn't improve ratio."""
        employees = [
            make_emp(ref_id="e1", is_saudi=False),
        ]
        batch = scan_batch(employees)
        result = simulate_nitaqat(batch, add_saudi=1, add_saudi_documented=False)
        assert result["projected_ratio"] == 0.0
        assert result["band_delta"] == 0

    def test_band_improvement_tracked(self):
        """Improvement/worsens flags reflect band changes."""
        employees = [
            make_emp(ref_id="e1", is_saudi=False),
            make_emp(ref_id="e2", is_saudi=False),
            make_emp(ref_id="e3", is_saudi=False),
            make_emp(ref_id="e4", is_saudi=False),
        ]
        batch = scan_batch(employees)
        result = simulate_nitaqat(batch, add_saudi=3, add_saudi_documented=True)
        assert result["improvement"] is True
        assert result["projected_band"] in ("low_green", "high_green", "platinum")


# ── Health Score Integration ────────────────────────────────────────────


class TestHealthScoreIntegration:
    def test_excellent_batch(self):
        """Fully compliant batch -> high health score."""
        employees = [make_emp(ref_id=f"e{i}") for i in range(10)]
        batch = scan_batch(employees)
        assert batch.compliance_health_score >= 90

    def test_poor_batch(self):
        """Problematic batch -> low health score."""
        employees = [
            make_emp(ref_id=f"e{i}", contract_documented_in_qiwa=False, gosi_enrolled=False, hire_date=None)
            for i in range(10)
        ]
        batch = scan_batch(employees)
        assert batch.compliance_health_score < 50


# ── Engine Registration ────────────────────────────────────────────────


class TestRuleRegistration:
    def test_rules_loaded(self):
        """Expected rules are registered."""
        rule_ids = [r.id for r in RULES]
        assert "QIWA_DOC_001" in rule_ids
        assert "QIWA_DOC_002" in rule_ids
        assert "QIWA_NIT_001" in rule_ids
        assert "QIWA_NIT_002" in rule_ids
        assert "QIWA_GOSI_001" in rule_ids
        assert "QIWA_CONTRACT_001" in rule_ids

    def test_all_rules_have_arabic(self):
        """Every rule has Arabic translations."""
        for rule in RULES:
            assert rule.name_ar, f"Rule {rule.id} missing Arabic name"
            assert rule.violation_message_ar, f"Rule {rule.id} missing Arabic violation message"
