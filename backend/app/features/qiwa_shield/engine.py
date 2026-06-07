"""
Qiwa Shield — Rule-Based Compliance Engine
Extensible rule system for Qiwa contract documentation + Nitaqat validation.
Core logic for the Documentation Shield feature.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Callable


# ── Types ──

class DocumentStatus(str, Enum):
    DOCUMENTED = "documented"       # 🟢 Qiwa contract exists, counts for Saudization
    MISSING = "missing"             # 🟡 No Qiwa contract, doesn't count
    AT_RISK = "at_risk"             # 🔴 Approaching 90-day runaway flag
    EXPIRED = "expired"             # 🔴 Contract expired


class NitaqatBand(str, Enum):
    PLATINUM = "platinum"
    HIGH_GREEN = "high_green"
    LOW_GREEN = "low_green"
    RED = "red"


@dataclass
class EmployeeRecord:
    """Single employee record for Qiwa Shield scanning."""
    ref_id: str
    employee_name: str
    employee_name_ar: str = ""
    iqama_number: str = ""
    nationality: str = ""
    is_saudi: bool = False
    basic_salary: Decimal = Decimal("0")
    total_gross_wage: Decimal = Decimal("0")
    job_title: str = ""
    ssco_code: str = ""
    hire_date: date | None = None
    contract_end_date: date | None = None
    contract_documented_in_qiwa: bool = False
    gosi_enrolled: bool = False
    gosi_enrollment_date: date | None = None
    monthly_hours: int = 0
    housing_allowance: Decimal = Decimal("0")
    violations: list[str] = field(default_factory=list)


@dataclass
class ComplianceRule:
    """A single extensible compliance rule."""
    id: str
    name: str
    name_ar: str
    description: str
    severity: str  # "blocker" | "warning" | "info"
    check_fn: Callable[[EmployeeRecord], bool]
    violation_message: str
    violation_message_ar: str


# ── Rule Definitions ──

RULES: list[ComplianceRule] = []


def _register(rule: ComplianceRule):
    RULES.append(rule)


_register(ComplianceRule(
    id="QIWA_DOC_001",
    name="Qiwa Contract Documentation",
    name_ar="توثيق العقد في قوى",
    description="Saudi employee must have a Qiwa-documented contract for Saudization credit. GOSI-only is not sufficient (post April 15, 2026 rule).",
    severity="blocker",
    check_fn=lambda e: e.is_saudi and not e.contract_documented_in_qiwa,
    violation_message="Saudi employee lacks Qiwa-documented contract. GOSI registration alone does not qualify for Saudization credit.",
    violation_message_ar="الموظف السعودي ليس لديه عقد موثق في قوى. التسجيل في التأمينات الاجتماعية وحده لا يؤهله لاحتساب نسب التوطين.",
))

_register(ComplianceRule(
    id="QIWA_DOC_002",
    name="90-Day Runaway Warning",
    name_ar="تحذير بلاغ هروب 90 يوم",
    description="Employees with undocumented contracts approaching 90 days from hire are at risk of automatic 'runaway worker' flag.",
    severity="blocker",
    check_fn=lambda e: (
        e.is_saudi
        and not e.contract_documented_in_qiwa
        and e.hire_date
        and (datetime.now().date() - e.hire_date).days >= 80
    ),
    violation_message="Employee approaching 90-day undocumented threshold. Automatic 'runaway worker' (بلاغ هروب) flag imminent.",
    violation_message_ar="الموظف يقترب من حد 90 يوماً بدون عقد موثق. سيتم تفعيل بلاغ هروب تلقائياً.",
))

_register(ComplianceRule(
    id="QIWA_NIT_001",
    name="Saudization Credit Eligibility",
    name_ar="أهلية احتساب نسب التوطين",
    description="Saudi employee must meet all three criteria: Qiwa-documented contract + GOSI enrollment + wage ≥ SAR 4,000.",
    severity="blocker",
    check_fn=lambda e: (
        e.is_saudi
        and (
            not e.contract_documented_in_qiwa
            or not e.gosi_enrolled
            or e.total_gross_wage < Decimal("4000")
        )
    ),
    violation_message="Saudi employee ineligible for Saudization credit. Requires: Qiwa contract + GOSI + min SAR 4,000.",
    violation_message_ar="الموظف السعودي غير مؤهل لاحتساب نسب التوطين. يتطلب: عقد قوى + تأمينات + حد أدنى ٤,٠٠٠ ريال.",
))

_register(ComplianceRule(
    id="QIWA_NIT_002",
    name="Nitaqat Weight Below 1.0",
    name_ar="وزن نطاق أقل من 1.0",
    description="Saudi employee earning between SAR 3,000–3,999 receives only 0.5 Nitaqat weight.",
    severity="warning",
    check_fn=lambda e: (
        e.is_saudi
        and e.contract_documented_in_qiwa
        and Decimal("3000") <= e.total_gross_wage < Decimal("4000")
    ),
    violation_message="Saudi employee has reduced Nitaqat weight (0.5). Increase wage to SAR 4,000+ for full weight.",
    violation_message_ar="وزن الموظف السعودي في نطاق منخفض (0.5). قم بزيادة الراتب إلى ٤,٠٠٠ ريال+ للحصول على الوزن الكامل.",
))

_register(ComplianceRule(
    id="QIWA_GOSI_001",
    name="GOSI Enrollment Missing",
    name_ar="التسجيل في التأمينات مفقود",
    description="Saudi employee must be enrolled in GOSI for Saudization credit. Missing enrollment blocks credit.",
    severity="blocker",
    check_fn=lambda e: e.is_saudi and not e.gosi_enrolled,
    violation_message="Saudi employee not enrolled in GOSI. Enrollment is mandatory for Saudization credit.",
    violation_message_ar="الموظف السعودي غير مسجل في التأمينات الاجتماعية. التسجيل إلزامي لاحتساب نسب التوطين.",
))

_register(ComplianceRule(
    id="QIWA_CONTRACT_001",
    name="Contract Expiry Warning",
    name_ar="تحذير انتهاء العقد",
    description="Employee contract is expiring within 30 days.",
    severity="warning",
    check_fn=lambda e: (
        e.contract_end_date
        and 0 <= (e.contract_end_date - datetime.now().date()).days <= 30
    ),
    violation_message="Employee contract expiring within 30 days. Renew before expiry to maintain compliance.",
    violation_message_ar="عقد الموظف سينتهي خلال ٣٠ يوماً. قم بالتجديد قبل انتهاء العقد للحفاظ على الامتثال.",
))


# ── Core Engine ──

@dataclass
class ScanResult:
    """Result of scanning a single employee against all rules."""
    employee: EmployeeRecord
    violations: list[ComplianceRule] = field(default_factory=list)
    document_status: DocumentStatus = DocumentStatus.DOCUMENTED
    nitaqat_weight: float = 0.0
    can_count_for_saudization: bool = False
    estimated_penalty_savings: Decimal = Decimal("0")


@dataclass
class BatchScanResult:
    """Result of scanning a batch of employees."""
    company_name: str = ""
    scan_id: str = ""
    scanned_at: str = ""
    total_employees: int = 0
    saudi_count: int = 0
    documented_count: int = 0
    undocumented_count: int = 0
    at_risk_count: int = 0
    total_violations: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    saudization_ratio: float = 0.0
    current_nitaqat_band: NitaqatBand = NitaqatBand.RED
    compliance_health_score: int = 0
    estimated_penalty_exposure: float = 0.0
    employees: list[ScanResult] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    estimated_penalty_savings: float = 0.0


def _calculate_nitaqat_weight(emp: EmployeeRecord) -> float:
    """Calculate Nitaqat weight for a single employee."""
    if not emp.is_saudi:
        return 0.0
    if not emp.contract_documented_in_qiwa or not emp.gosi_enrolled:
        return 0.0
    if emp.monthly_hours >= 160:
        return 1.0
    if emp.total_gross_wage >= Decimal("4000"):
        return 1.0
    if Decimal("3000") <= emp.total_gross_wage < Decimal("4000"):
        return 0.5
    return 0.0


def _classify_nitaqat_band(ratio: float) -> NitaqatBand:
    """Classify Nitaqat band from ratio. Post-2026 overhaul: Yellow eliminated, direct Red."""
    if ratio >= 40:
        return NitaqatBand.PLATINUM
    elif ratio >= 35:
        return NitaqatBand.HIGH_GREEN
    elif ratio >= 26:
        return NitaqatBand.LOW_GREEN
    return NitaqatBand.RED


def _calculate_health_score(
    total: int,
    documented: int,
    blocker_count: int,
    warning_count: int,
    saudization_ratio: float,
    band: NitaqatBand,
) -> int:
    """Calculate compliance health score 0-100."""
    if total == 0:
        return 100  # No employees, no violations
    score = 100
    doc_pct = (documented / total * 100) if total > 0 else 0
    # Deductions
    if doc_pct < 90:
        score -= 20
    if doc_pct < 80:
        score -= 15
    score -= blocker_count * 8
    score -= warning_count * 3
    if saudization_ratio < 18:
        score -= 25
    elif saudization_ratio < 26:
        score -= 15
    if band == NitaqatBand.RED:
        score -= 20
    return max(0, min(100, score))


def scan_employee(emp: EmployeeRecord) -> ScanResult:
    """Run all rules against a single employee."""
    result = ScanResult(employee=emp)
    violations = []

    for rule in RULES:
        try:
            if rule.check_fn(emp):
                violations.append(rule)
                emp.violations.append(rule.id)
        except Exception:
            pass  # Skip broken rules

    result.violations = violations
    result.nitaqat_weight = _calculate_nitaqat_weight(emp)

    # Determine document status
    if emp.is_saudi:
        if not emp.contract_documented_in_qiwa:
            if emp.hire_date and (datetime.now().date() - emp.hire_date).days >= 80:
                result.document_status = DocumentStatus.AT_RISK
            else:
                result.document_status = DocumentStatus.MISSING
        elif emp.contract_end_date and emp.contract_end_date < datetime.now().date():
            result.document_status = DocumentStatus.EXPIRED

    # Can this employee count for Saudization?
    result.can_count_for_saudization = (
        emp.is_saudi
        and emp.contract_documented_in_qiwa
        and emp.gosi_enrolled
        and emp.total_gross_wage >= Decimal("4000")
    )

    # Estimate penalty savings per violation
    result.estimated_penalty_savings = Decimal(str(len(violations))) * Decimal("5000")

    return result


def scan_batch(
    employees: list[EmployeeRecord],
    company_name: str = "",
) -> BatchScanResult:
    """Run all rules against a batch of employees."""
    import uuid

    results = [scan_employee(emp) for emp in employees]

    total = len(results)
    saudi_count = sum(1 for r in results if r.employee.is_saudi)
    documented_count = sum(1 for r in results if r.employee.is_saudi and r.employee.contract_documented_in_qiwa)
    undocumented_count = sum(1 for r in results if r.employee.is_saudi and not r.employee.contract_documented_in_qiwa)
    at_risk_count = sum(1 for r in results if r.document_status == DocumentStatus.AT_RISK)
    total_violations = sum(len(r.violations) for r in results)
    blocker_count = sum(1 for r in results for v in r.violations if v.severity == "blocker")
    warning_count = sum(1 for r in results for v in r.violations if v.severity == "warning")

    # Saudization ratio
    saudi_weight_sum = sum(Decimal(str(r.nitaqat_weight)) for r in results)
    saudization_ratio = float(saudi_weight_sum / Decimal(str(max(total, 1))) * Decimal("100"))
    band = _classify_nitaqat_band(saudization_ratio)

    # Health score
    health_score = _calculate_health_score(total, documented_count, blocker_count, warning_count, saudization_ratio, band)

    # Penalty exposure
    estimated_penalty = float(blocker_count * 10000 + warning_count * 3000)
    estimated_savings = float(sum(r.estimated_penalty_savings for r in results))

    # Generate action items
    action_items = []
    if undocumented_count > 0:
        action_items.append(f"Document {undocumented_count} Saudi employee{'s' if undocumented_count > 1 else ''} in Qiwa immediately — they currently contribute zero to your Saudization ratio.")
    if at_risk_count > 0:
        action_items.append(f"URGENT: {at_risk_count} employee{'s' if at_risk_count > 1 else ''} approaching 90-day undocumented threshold — will trigger automatic runaway flag.")
    if saudization_ratio < 26:
        shortfall = 26 - saudization_ratio
        needed_hires = max(1, int(shortfall / 100 * total / 1.0) + 1)
        action_items.append(f"Your Nitaqat band is {band.value}. Hire approximately {needed_hires} additional documented Saudi employees to reach Low Green.")
    if blocker_count > 0:
        action_items.append(f"Resolve {blocker_count} blocker{'s' if blocker_count > 1 else ''} — these carry penalty risk of up to SAR {estimated_penalty:,.0f}.")

    return BatchScanResult(
        company_name=company_name,
        scan_id=f"qs-{uuid.uuid4().hex[:8]}",
        scanned_at=datetime.utcnow().isoformat() + "Z",
        total_employees=total,
        saudi_count=saudi_count,
        documented_count=documented_count,
        undocumented_count=undocumented_count,
        at_risk_count=at_risk_count,
        total_violations=total_violations,
        blocker_count=blocker_count,
        warning_count=warning_count,
        saudization_ratio=round(saudization_ratio, 1),
        current_nitaqat_band=band,
        compliance_health_score=health_score,
        estimated_penalty_exposure=round(estimated_penalty, 2),
        employees=results,
        action_items=action_items,
        estimated_penalty_savings=round(estimated_savings, 2),
    )


def simulate_nitaqat(
    current_batch: BatchScanResult,
    add_saudi: int = 0,
    add_saudi_documented: bool = True,
    increase_salaries_for: list[str] | None = None,
) -> dict:
    """
    Simulate Nitaqat band impact of workforce changes.
    Returns projected ratio, band, and deltas.
    """
    # Start from current state
    current_weight = sum(Decimal(str(e.nitaqat_weight)) for e in current_batch.employees)
    #Hmm total is the number of employees
    total = len(current_batch.employees)

    # Add new Saudis
    new_weight = current_weight
    for _ in range(add_saudi):
        if add_saudi_documented:
            new_weight += Decimal("1.0")
        else:
            new_weight += Decimal("0.0")

    new_total = total + add_saudi
    projected_ratio = float(new_weight / Decimal(str(max(new_total, 1))) * Decimal("100"))
    projected_band = _classify_nitaqat_band(projected_ratio)

    band_priority = {b.value: i for i, b in enumerate(NitaqatBand)}
    current_priority = band_priority.get(current_batch.current_nitaqat_band.value, 5)
    projected_priority = band_priority.get(projected_band.value, 5)

    return {
        "current_ratio": current_batch.saudization_ratio,
        "current_band": current_batch.current_nitaqat_band.value,
        "projected_ratio": round(projected_ratio, 1),
        "projected_band": projected_band.value,
        "improvement": projected_priority < current_priority,
        "worsens": projected_priority > current_priority,
        "band_delta": projected_priority - current_priority,
        "health_score_impact": 5 * add_saudi if add_saudi_documented else 0,
        "new_saudi_hires": add_saudi,
    }