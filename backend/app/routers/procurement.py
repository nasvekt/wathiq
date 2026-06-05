"""
Wathiq — Procurement Saudization endpoints.
Blueprint Section 4B — Primary Market Wedge (May 31, 2026 enforcement).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from app.engines.procurement_engine import (
    is_procurement_role,
    calculate_procurement_saudization,
    check_title_duties_mismatch,
    PROCUREMENT_ROLES,
)

router = APIRouter()


class ProcurementEmployee(BaseModel):
    ref_id: str
    ssco_code: Optional[str] = None
    nationality: str = ""
    basic_salary: Decimal = Decimal("0")
    total_gross_wage: Optional[Decimal] = None
    monthly_hours: Optional[int] = None
    raw_job_title: Optional[str] = None


class ProcurementScanRequest(BaseModel):
    company_name: str = ""
    sector_code: str = "technology"
    employees: list[ProcurementEmployee]


class MismatchCheckRequest(BaseModel):
    employee: ProcurementEmployee
    activity_evidence: list[str] = []


@router.post("/procurement/scan")
async def procurement_scan(request: ProcurementScanRequest):
    """
    Procurement Quick Scan — simplified entry point for small companies.
    SAR 500/scan or included in annual plans. Free trial conversion mechanism.
    """
    try:
        # Filter to procurement roles only
        proc_employees = [
            emp.model_dump() for emp in request.employees
            if is_procurement_role(emp.ssco_code)
        ]

        if len(proc_employees) < 3:
            return {
                "compliant": True,
                "message": "Less than 3 procurement employees — rule does not apply",
                "procurement_headcount": len(proc_employees),
                "roles_found": list(set(
                    PROCUREMENT_ROLES.get(e.get("ssco_code", ""), {}).get("title_en", e.get("ssco_code", ""))
                    for e in proc_employees
                )),
            }

        # Calculate procurement Saudization
        result = calculate_procurement_saudization(proc_employees)

        # Get role breakdown
        roles = {}
        for emp in proc_employees:
            code = emp.get("ssco_code", "")
            info = PROCUREMENT_ROLES.get(code, {})
            role_name = info.get("title_en", code)
            if role_name not in roles:
                roles[role_name] = {"ssco_code": code, "count": 0, "saudi_count": 0}
            roles[role_name]["count"] += 1
            if (emp.get("nationality") or "").strip().lower() in ("saudi", "saudi arabia", "sa"):
                roles[role_name]["saudi_count"] += 1

        return {
            **result,
            "procurement_headcount": len(proc_employees),
            "roles": roles,
            "scan_type": "quick",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan error: {str(e)}")


@router.post("/procurement/mismatch-check")
async def mismatch_check(request: MismatchCheckRequest):
    """
    Title-Duties Mismatch Detector.
    Flags employees whose actual duties don't match their registered title.
    """
    try:
        emp_dict = request.employee.model_dump()
        result = check_title_duties_mismatch(emp_dict, request.activity_evidence)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mismatch check error: {str(e)}")


@router.get("/procurement/roles")
async def procurement_roles():
    """List all 12 procurement roles with SSCO codes and salary floors."""
    return {
        "roles": [
            {"ssco_code": code, **info}
            for code, info in PROCUREMENT_ROLES.items()
        ],
        "enforcement_date": "2026-05-31",
        "required_saudization_pct": 70.0,
        "minimum_headcount_for_rule": 3,
    }