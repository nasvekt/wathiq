"""
End-to-end integration tests for the Master Compliance Engine.

Tests cover:
- Single Saudi employee all clear
- Single expat employee all clear
- Employee with multiple violations
- Batch validation with correct counts
- Batch Saudization ratio
- GOSI null enrollment blocked
- Iqama expired blocked
- WPS floor blocked
"""

from datetime import date
from decimal import Decimal

import pytest

from app.engines.compliance_engine import validate_batch, validate_employee
from app.schemas.compliance import (
    ComplianceStatus,
    EmployeeInput,
)


# ── Helper to build employee inputs ────────────────────────────────────


def make_saudi_employee(
    ref_id="EMP001",
    basic_salary=Decimal("10000.00"),
    housing_allowance=Decimal("2500.00"),
    transport_allowance=Decimal("0.00"),
    other_allowances=Decimal("0.00"),
    iqama_expiry_date=date(2027, 1, 1),
    date_of_birth=date(1990, 1, 1),
    gosi_enrollment_date=date(2024, 1, 1),
    hire_date=date(2025, 1, 1),
    ssco_code=None,
    contract_published=True,
    registered_gosi_contract_salary=None,
    monthly_hours=None,
) -> EmployeeInput:
    return EmployeeInput(
        ref_id=ref_id,
        employee_name="Ahmed Ali",
        iqama_number="1000000001",
        nationality="Saudi",
        basic_salary=basic_salary,
        housing_allowance=housing_allowance,
        transport_allowance=transport_allowance,
        other_allowances=other_allowances,
        iqama_expiry_date=iqama_expiry_date,
        date_of_birth=date_of_birth,
        gosi_enrollment_date=gosi_enrollment_date,
        hire_date=hire_date,
        ssco_code=ssco_code,
        contract_published=contract_published,
        registered_gosi_contract_salary=registered_gosi_contract_salary,
        monthly_hours=monthly_hours,
    )


def make_expat_employee(
    ref_id="EMP002",
    basic_salary=Decimal("5000.00"),
    housing_allowance=Decimal("1000.00"),
    transport_allowance=Decimal("0.00"),
    other_allowances=Decimal("0.00"),
    iqama_expiry_date=date(2027, 1, 1),
    hire_date=date(2025, 1, 1),
    contract_published=True,
    registered_gosi_contract_salary=None,
) -> EmployeeInput:
    return EmployeeInput(
        ref_id=ref_id,
        employee_name="John Smith",
        iqama_number="2000000001",
        nationality="Egyptian",
        basic_salary=basic_salary,
        housing_allowance=housing_allowance,
        transport_allowance=transport_allowance,
        other_allowances=other_allowances,
        iqama_expiry_date=iqama_expiry_date,
        hire_date=hire_date,
        contract_published=contract_published,
        registered_gosi_contract_salary=registered_gosi_contract_salary,
    )


REFERENCE_DATE = date(2026, 5, 15)


# ── Single Employee Tests ──────────────────────────────────────────────


class TestSingleEmployee:
    def test_single_saudi_employee_all_clear(self):
        """Saudi employee with all fields correct → READY."""
        emp = make_saudi_employee()
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.READY
        assert result.flags == []
        assert result.nationalization.nitaqat_weight == Decimal("1.0")
        assert result.gosi.gosi_scheme == "progressive"

    def test_single_expat_employee_all_clear(self):
        """Expat employee with all fields correct → READY."""
        emp = make_expat_employee()
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.READY
        assert result.flags == []
        assert result.nationalization.nitaqat_weight == Decimal("0.0")
        assert result.gosi.gosi_scheme == "expat"

    def test_employee_with_multiple_violations(self):
        """Employee with expired Iqama + WPS floor violation → BLOCKED."""
        emp = make_saudi_employee(
            basic_salary=Decimal("2000.00"),
            housing_allowance=Decimal("0.00"),
            iqama_expiry_date=date(2026, 4, 1),  # expired
            contract_published=False,
            hire_date=date(2026, 3, 1),  # 75 days ago → violation
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.BLOCKED
        assert "IQAMA_EXPIRED" in result.flags
        assert "WPS_FLOOR_VIOLATION" in result.flags
        assert "QIWA_CONTRACT_WINDOW_VIOLATION" in result.flags

    def test_employee_with_review_flags(self):
        """Employee with housing zero → REVIEW."""
        emp = make_saudi_employee(
            housing_allowance=Decimal("0.00"),
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.REVIEW
        assert "HOUSING_ZERO" in result.flags

    def test_employee_gosi_null_enrollment_blocked(self):
        """Saudi with no GOSI enrollment date → BLOCKED."""
        emp = make_saudi_employee(
            gosi_enrollment_date=None,
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.BLOCKED
        assert "GOSI_ENROLLMENT_DATE_MISSING" in result.flags

    def test_employee_iqama_expired_blocked(self):
        """Employee with expired Iqama → BLOCKED."""
        emp = make_saudi_employee(
            iqama_expiry_date=date(2026, 4, 1),
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.BLOCKED
        assert "IQAMA_EXPIRED" in result.flags

    def test_employee_wps_floor_blocked(self):
        """Saudi with gross < 4000 → WPS floor violation → BLOCKED."""
        emp = make_saudi_employee(
            basic_salary=Decimal("3000.00"),
            housing_allowance=Decimal("500.00"),
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.BLOCKED
        assert "WPS_FLOOR_VIOLATION" in result.flags

    def test_expat_wps_floor_blocked(self):
        """Expat with gross < 3200 → WPS floor violation → BLOCKED."""
        emp = make_expat_employee(
            basic_salary=Decimal("2000.00"),
            housing_allowance=Decimal("500.00"),
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.BLOCKED
        assert "WPS_FLOOR_VIOLATION" in result.flags

    def test_employee_iqama_expiring_30d(self):
        """Employee with Iqama expiring in 30 days → REVIEW."""
        emp = make_saudi_employee(
            iqama_expiry_date=date(2026, 6, 14),  # 30 days from ref
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert "IQAMA_EXPIRING_30D" in result.flags

    def test_employee_contract_warning(self):
        """Employee with contract warning → REVIEW."""
        emp = make_saudi_employee(
            contract_published=False,
            hire_date=date(2026, 4, 20),  # 25 days ago
        )
        result = validate_employee(emp, reference_date=REFERENCE_DATE)
        assert result.status == ComplianceStatus.REVIEW
        assert "QIWA_CONTRACT_WINDOW_WARNING" in result.flags


# ── Batch Validation Tests ─────────────────────────────────────────────


class TestBatchValidation:
    def test_batch_validation_produces_correct_counts(self):
        """Batch with mixed statuses produces correct ready/review/blocked counts."""
        employees = [
            make_saudi_employee(ref_id="EMP001"),  # READY
            make_expat_employee(ref_id="EMP002"),  # READY
            make_saudi_employee(ref_id="EMP003", housing_allowance=Decimal("0.00")),  # REVIEW
            make_saudi_employee(ref_id="EMP004", iqama_expiry_date=date(2026, 4, 1)),  # BLOCKED
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        assert result.success is True
        assert result.summary.total_processed == 4
        assert result.summary.ready_count == 2
        assert result.summary.review_count == 1
        assert result.summary.blocked_count == 1

    def test_batch_saudization_ratio(self):
        """Batch Saudization ratio calculated correctly."""
        employees = [
            make_saudi_employee(ref_id="EMP001"),  # weight 1.0
            make_saudi_employee(ref_id="EMP002"),  # weight 1.0
            make_expat_employee(ref_id="EMP003"),  # weight 0.0
            make_expat_employee(ref_id="EMP004"),  # weight 0.0
            make_expat_employee(ref_id="EMP005"),  # weight 0.0
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        # 2 Saudis at full weight / 5 total = 40.0%
        assert result.workforce_analytics.saudization_ratio == Decimal("40.00")

    def test_batch_all_saudis(self):
        """All Saudi batch → 100% Saudization."""
        employees = [
            make_saudi_employee(ref_id=f"EMP{i:03d}") for i in range(5)
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        assert result.workforce_analytics.saudization_ratio == Decimal("100.00")

    def test_batch_all_expat(self):
        """All expat batch → 0% Saudization."""
        employees = [
            make_expat_employee(ref_id=f"EMP{i:03d}") for i in range(5)
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        assert result.workforce_analytics.saudization_ratio == Decimal("0.00")

    def test_batch_nitaqat_band(self):
        """Batch with 40% Saudization in technology → platinum."""
        employees = [
            make_saudi_employee(ref_id=f"S{i:03d}") for i in range(4)
        ] + [
            make_expat_employee(ref_id=f"E{i:03d}") for i in range(6)
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        # 4/10 = 40% → platinum for technology medium_a
        assert result.workforce_analytics.nitaqat_band == "platinum"

    def test_batch_nitaqat_band_red(self):
        """Batch with very low Saudization → red band."""
        employees = [
            make_saudi_employee(ref_id="S001"),  # 1 Saudi
        ] + [
            make_expat_employee(ref_id=f"E{i:03d}") for i in range(19)  # 19 expats
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        # 1/20 = 5% → red
        assert result.workforce_analytics.nitaqat_band == "red"

    def test_batch_health_score(self):
        """Batch health score reflects blocked/review counts."""
        employees = [
            make_saudi_employee(ref_id="EMP001"),  # READY
            make_saudi_employee(ref_id="EMP002", iqama_expiry_date=date(2026, 6, 1)),  # BLOCKED (WPS floor)
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        # 1 review (-5) + 1 iqama expiring 30d (-5) = 90
        assert result.summary.company_health_score == 90

    def test_batch_penalty_exposure(self):
        """Batch penalty exposure calculated from blocked/review counts."""
        employees = [
            make_saudi_employee(ref_id="EMP001"),  # READY
            make_saudi_employee(ref_id="EMP002", iqama_expiry_date=date(2026, 4, 1)),  # BLOCKED
            make_saudi_employee(ref_id="EMP003", housing_allowance=Decimal("0.00")),  # REVIEW
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        # 1 blocked * 5000 + 1 review * 1500 = 6500
        assert result.summary.penalty_exposure == Decimal("6500.00")

    def test_batch_gosi_liability(self):
        """Batch total GOSI liability is sum of all employee contributions."""
        employees = [
            make_saudi_employee(
                ref_id="EMP001",
                basic_salary=Decimal("10000.00"),
                housing_allowance=Decimal("2500.00"),
            ),
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        # Single employee: GOSI total contribution
        expected_gosi = employees[0].basic_salary + employees[0].housing_allowance  # 12500
        # 12500 * 0.23 (progressive rate May 2026) = 2875.00
        assert result.workforce_analytics.total_gosi_liability == Decimal("2875.00")

    def test_batch_transaction_id_present(self):
        """Batch response includes transaction_id and processed_at."""
        employees = [make_saudi_employee()]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        assert result.transaction_id.startswith("tx-")
        assert result.processed_at.endswith("Z")

    def test_batch_records_match_input(self):
        """Batch returns one result per input employee."""
        employees = [
            make_saudi_employee(ref_id="EMP001"),
            make_expat_employee(ref_id="EMP002"),
            make_saudi_employee(ref_id="EMP003"),
        ]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        assert len(result.records) == 3
        assert result.records[0].ref_id == "EMP001"
        assert result.records[1].ref_id == "EMP002"
        assert result.records[2].ref_id == "EMP003"

    def test_batch_single_employee(self):
        """Batch with single employee works correctly."""
        employees = [make_saudi_employee()]
        result = validate_batch(
            employees,
            sector_code="technology",
            size_category="medium_a",
            reference_date=REFERENCE_DATE,
        )
        assert result.summary.total_processed == 1
        assert result.summary.ready_count == 1
        assert result.summary.blocked_count == 0
        assert result.summary.review_count == 0
