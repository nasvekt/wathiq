"""
Master Compliance Engine.
Orchestrates all 10 compliance rule engines for a single employee.
Pure deterministic pipeline — no AI calls.

This is the core of Wathiq. Every employee record passes through here.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from app.schemas.compliance import (
    EmployeeInput,
    EmployeeResult,
    ComplianceStatus,
    GOSIResult,
    NitaqatResult,
    ContractStatus,
    ComplianceValidationResponse,
    ComplianceSummary,
    WorkforceAnalytics,
)
from app.engines.gosi_engine import calculate_gosi_contribution
from app.engines.nitaqat_engine import (
    calculate_nitaqat_weight,
    calculate_saudization_ratio,
    classify_nitaqat_band,
)
from app.engines.wps_engine import check_wps_floor, check_wps_variance
from app.engines.housing_engine import check_housing_allowance
from app.engines.iqama_engine import check_iqama_expiry
from app.engines.engineer_wage_engine import check_engineer_wage_floor
from app.engines.contract_engine import check_contract_window
from app.engines.penalty_engine import calculate_health_score, calculate_penalty_exposure
from app.engines.diversity_engine import check_diversity_cap


def _is_saudi(nationality: str) -> bool:
    return nationality.strip().lower() in ("saudi", "saudi arabia", "sa")


def validate_employee(
    employee: EmployeeInput,
    reference_date: date | None = None,
) -> EmployeeResult:
    """
    Run all 10 compliance rules against a single employee record.
    """
    ref = reference_date or date.today()
    flags = []
    blocked = False
    review = False

    # Rule 1: Iqama Expiry
    iqama_check = check_iqama_expiry(employee.iqama_expiry_date, ref)
    if iqama_check["status"] == "expired":
        flags.append("IQAMA_EXPIRED")
        blocked = True
    elif iqama_check["status"] == "at_risk":
        flags.append(f"IQAMA_EXPIRING_{iqama_check['alert_level']}D")

    # Total gross wage
    total_gross = (
        employee.basic_salary
        + employee.housing_allowance
        + employee.transport_allowance
        + employee.other_allowances
    )

    # Rule 2: Nitaqat Weight
    nitaqat_weight = calculate_nitaqat_weight(
        nationality=employee.nationality,
        total_gross_wage=total_gross,
        monthly_hours=employee.monthly_hours,
    )

    # Rule 4: WPS Floor
    wps_floor = check_wps_floor(employee.nationality, total_gross)
    if not wps_floor["passed"]:
        flags.append("WPS_FLOOR_VIOLATION")
        blocked = True

    if employee.registered_gosi_contract_salary:
        wps_var = check_wps_variance(total_gross, employee.registered_gosi_contract_salary)
        if not wps_var["passed"]:
            flags.append("WPS_VARIANCE_VIOLATION")
            review = True

    # Rule 5: Housing Allowance
    housing = check_housing_allowance(employee.basic_salary, employee.housing_allowance)
    if housing["flags"]:
        flags.extend(housing["flags"])
        if "HOUSING_ZERO" in housing["flags"]:
            review = True

    # Rule 6: GOSI
    gosi_result = calculate_gosi_contribution(
        nationality=employee.nationality,
        basic_salary=employee.basic_salary,
        housing_allowance=employee.housing_allowance,
        date_of_birth=employee.date_of_birth,
        gosi_enrollment_date=employee.gosi_enrollment_date,
        reference_date=ref,
    )

    if _is_saudi(employee.nationality) and not employee.gosi_enrollment_date:
        flags.append("GOSI_ENROLLMENT_DATE_MISSING")
        blocked = True

    # Rule 8: Engineer Wage Floor
    engineer_check = check_engineer_wage_floor(
        nationality=employee.nationality,
        ssco_code=employee.ssco_code,
        basic_salary=employee.basic_salary,
    )
    if engineer_check["flags"]:
        flags.extend(engineer_check["flags"])
        review = True

    # Rule 9: Qiwa Contract Window
    contract = check_contract_window(
        hire_date=employee.hire_date,
        contract_published=employee.contract_published,
        reference_date=ref,
    )
    if contract["status"] == "violation":
        flags.append("QIWA_CONTRACT_WINDOW_VIOLATION")
        review = True
    elif contract["status"] == "warning":
        flags.append("QIWA_CONTRACT_WINDOW_WARNING")

    # Determine final status
    if blocked:
        status = ComplianceStatus.BLOCKED
    elif review or flags:
        status = ComplianceStatus.REVIEW
    else:
        status = ComplianceStatus.READY

    return EmployeeResult(
        ref_id=employee.ref_id,
        employee_name=employee.employee_name,
        iqama_number=employee.iqama_number,
        status=status,
        ssco_classification=(
            {"code": employee.ssco_code, "confidence": None}
            if employee.ssco_code
            else None
        ),
        financials={
            "total_gross_wage": total_gross.quantize(Decimal("0.01")),
            "basic_salary": employee.basic_salary,
            "housing_allowance": employee.housing_allowance,
            "transport_allowance": employee.transport_allowance,
            "other_allowances": employee.other_allowances,
        },
        nationalization=NitaqatResult(
            nitaqat_weight=nitaqat_weight,
            wage_floor_applied=engineer_check.get("wage_floor_applied", "general_4000"),
        ),
        contract_status=ContractStatus(
            qiwa_days_elapsed=contract.get("days_elapsed"),
            qiwa_contract_flag=contract["status"],
        ),
        flags=flags,
        gosi=GOSIResult(
            gosi_wage_base=gosi_result["gosi_wage_base"],
            gosi_scheme=gosi_result["gosi_scheme"],
            gosi_rate=gosi_result["gosi_rate"],
            total_contribution=gosi_result["total_contribution"],
            employer_contribution=gosi_result["employer_contribution"],
            employee_deduction=gosi_result["employee_deduction"],
        ),
    )


def validate_batch(
    employees: list[EmployeeInput],
    sector_code: str = "technology",
    size_category: str = "medium_a",
    reference_date: date | None = None,
) -> ComplianceValidationResponse:
    """
    Validate a batch of employees. Main entry point for /validate/compliance.
    """
    ref = reference_date or date.today()
    transaction_id = f"tx-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

    results = [validate_employee(emp, ref) for emp in employees]

    ready_count = sum(1 for r in results if r.status == ComplianceStatus.READY)
    review_count = sum(1 for r in results if r.status == ComplianceStatus.REVIEW)
    blocked_count = sum(1 for r in results if r.status == ComplianceStatus.BLOCKED)

    saudi_weight_sum = sum(r.nationalization.nitaqat_weight for r in results)
    saudization_ratio = calculate_saudization_ratio(len(results), saudi_weight_sum)
    nitaqat_band = classify_nitaqat_band(saudization_ratio, sector_code, size_category)
    total_gosi = sum(r.gosi.total_contribution for r in results)

    iqama_expiring_30 = sum(1 for r in results if "IQAMA_EXPIRING_30D" in r.flags)
    iqama_expired = sum(1 for r in results if "IQAMA_EXPIRED" in r.flags)

    red_band = nitaqat_band == "red"
    health = calculate_health_score(
        blocked_count=blocked_count,
        review_count=review_count,
        red_band=red_band,
        iqama_expiring_30_days=iqama_expiring_30,
        iqama_expired=iqama_expired,
    )
    penalty = calculate_penalty_exposure(blocked_count, review_count)

    return ComplianceValidationResponse(
        success=True,
        transaction_id=transaction_id,
        processed_at=datetime.utcnow().isoformat() + "Z",
        summary=ComplianceSummary(
            total_processed=len(results),
            ready_count=ready_count,
            review_count=review_count,
            blocked_count=blocked_count,
            company_health_score=health["score"],
            penalty_exposure=penalty,
        ),
        workforce_analytics=WorkforceAnalytics(
            saudization_ratio=saudization_ratio,
            nitaqat_band=nitaqat_band,
            total_gosi_liability=total_gosi.quantize(Decimal("0.01")),
            expat_diversity={
                **check_diversity_cap([
                    {
                        "nationality": e.nationality,
                        "is_saudi": _is_saudi(e.nationality),
                    }
                    for e in employees
                ]),
            },
        ),
        records=results,
    )
