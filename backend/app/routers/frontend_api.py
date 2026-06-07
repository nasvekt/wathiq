"""
Wathiq — Frontend-facing API endpoints with Supabase integration.
Queries real data by company_id, falls back to mock when empty.
"""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional
from app.database import select, insert, update, delete
from datetime import date
import uuid
import json

router = APIRouter()


def _get_company_id(request: Request) -> str:
    """Extract company_id from header or return dev ID."""
    return request.headers.get("x-company-id", "dev-company-001")


@router.get("/compliance/dashboard")
async def dashboard(request: Request):
    """Get dashboard summary for the authenticated company."""
    company_id = _get_company_id(request)

    try:
        batches = await select("audit_batches", {
            "company_id": f"eq.{company_id}",
            "order": "created_at.desc",
            "limit": "1",
        }, use_admin=True)
    except Exception:
        batches = []

    if batches:
        b = batches[0]
        return {
            "health_score": b.get("company_health_score", 74),
            "health_score_trend": "down",
            "nitaqat_band": b.get("nitaqat_band", "low_green"),
            "nitaqat_percentage": float(b.get("saudization_ratio", 0)) if b.get("saudization_ratio") else 28.5,
            "total_employees": b.get("total_records", 0),
            "ready_count": b.get("ready_count", 0),
            "review_count": b.get("review_count", 0),
            "blocked_count": b.get("blocked_count", 0),
            "at_risk_count": 0,
            "pending_count": 0,
            "penalty_exposure": float(b.get("penalty_exposure", 0)) if b.get("penalty_exposure") else 0,
            "total_gosi_liability": float(b.get("total_gosi_liability", 0)) if b.get("total_gosi_liability") else 0,
            "iqama_expiring_soon": 0,
            "last_audit_date": str(b.get("created_at", ""))[:10] if b.get("created_at") else "",
            "source": "supabase",
        }

    return {
        "health_score": 0, "health_score_trend": "stable",
        "nitaqat_band": "unknown", "nitaqat_percentage": 0,
        "total_employees": 0, "ready_count": 0, "review_count": 0,
        "blocked_count": 0, "at_risk_count": 0, "pending_count": 0,
        "penalty_exposure": 0, "total_gosi_liability": 0,
        "iqama_expiring_soon": 0, "last_audit_date": "",
        "source": "no_data",
        "message": "Upload your payroll to see compliance results.",
    }


@router.get("/compliance/employees")
async def employees(
    request: Request,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """Get employees for the authenticated company."""
    company_id = _get_company_id(request)

    try:
        params = {
            "company_id": f"eq.{company_id}",
            "limit": str(page_size),
            "offset": str((page - 1) * page_size),
        }
        if status:
            params["compliance_status"] = f"eq.{status}"
        results = await select("employee_records", params, use_admin=True)
    except Exception:
        results = []

    if results:
        mapped = [{
            "id": r.get("id", ""),
            "iqama": r.get("iqama_number", ""),
            "name_en": r.get("employee_name", ""),
            "name_ar": r.get("employee_name", ""),
            "nationality": r.get("nationality", "Saudi Arabia"),
            "job_title": r.get("raw_job_title", ""),
            "ssco_code": r.get("ssco_code", ""),
            "basic_salary": float(r.get("basic_salary", 0)) or 0,
            "housing_allowance": float(r.get("housing_allowance", 0)) or 0,
            "gross_salary": float(r.get("total_gross_wage", 0)) or 0,
            "status": r.get("compliance_status", "pending"),
            "flags": r.get("flags", []) or [],
        } for r in results]
        return {"total": len(mapped), "page": page, "page_size": page_size, "results": mapped}

    return {"total": 0, "page": page, "page_size": page_size, "results": []}


@router.get("/compliance/health-score")
async def health_score():
    return {"score": 0, "previous_score": 0, "change": 0, "trend": "stable"}


@router.get("/compliance/iqama-calendar")
async def iqama_calendar():
    return {"total_active": 0, "expiring_90_days": 0, "expiring_60_days": 0, "expiring_30_days": 0, "expired": 0, "upcoming": []}


@router.get("/compliance/contracts")
async def contract_tracker():
    return {"total_pending": 0, "warning_next_5_days": 0, "violations": 0, "upcoming": []}


@router.get("/compliance/trends")
async def compliance_trends(range: Optional[str] = "6m"):
    return {"health_score": [], "saudization": [], "gosi_liability": []}


@router.post("/simulator/nitaqat")
async def simulate_nitaqat():
    return {"current_ratio": 0, "current_band": "unknown", "projected_ratio": 0, "projected_band": "unknown", "band_drop_warning": False}


@router.get("/wage-sync/batches")
async def wage_batches(request: Request):
    company_id = _get_company_id(request)
    try:
        results = await select("audit_batches", {
            "company_id": f"eq.{company_id}",
            "order": "created_at.desc",
            "limit": "10",
        }, use_admin=True)
    except Exception:
        results = []

    if results:
        return {"batches": [
            {"id": r.get("id", ""), "period": r.get("payroll_period", ""), "status": r.get("status", ""),
             "records": r.get("total_records", 0), "created": str(r.get("created_at", ""))[:10] if r.get("created_at") else ""}
            for r in results
        ]}
    return {"batches": []}


@router.post("/wage-sync/export")
async def export_sif():
    return {"success": True, "sif_content": "", "sha256_hash": ""}


@router.get("/developer/keys")
async def get_api_keys():
    return {"keys": []}


@router.post("/developer/keys")
async def create_api_key(name: str = "Default"):
    return {"key": f"wath_dev_test", "prefix": "wath_dev", "name": name}


@router.delete("/developer/keys/{key_id}")
async def revoke_api_key(key_id: str):
    return {"success": True, "key_id": key_id}


@router.get("/billing")
async def billing_info():
    return {"plan": "free", "status": "active", "amount": 0, "currency": "SAR", "billing_cycle": "free", "next_billing": ""}


@router.get("/billing/invoices")
async def billing_invoices():
    return {"invoices": []}


@router.get("/founder/summary")
async def founder_summary():
    return {"total_companies": 0, "mrr": 0, "arr": 0, "records_processed": 0}


@router.get("/founder/users")
async def founder_users():
    return {"users": []}


# ── Seed data endpoint ──

@router.post("/seed/sample-data")
@router.get("/seed/sample-data")
async def seed_sample_data():
    """Seed Supabase with sample data for a test company."""
    company_id = "dev-company-001"
    batch_id = str(uuid.uuid4())

    # Create company
    try:
        existing = await select("companies", {"id": f"eq.{company_id}"}, use_admin=True)
        if not existing:
            await insert("companies", [{
                "id": company_id, "name": "ConstructCo Saudi Arabia",
                "name_ar": "شركة كونستركتكو السعودية",
                "commercial_registration": "CR-10101010", "email": "hr@constructco.sa",
                "economic_sector_code": "construction", "establishment_size_category": "medium_a",
                "total_headcount": 150, "plan_tier": "professional",
                "is_active": True, "onboarding_complete": True,
            }], use_admin=True)
    except Exception:
        pass

    # Create audit batch
    try:
        await insert("audit_batches", [{
            "id": batch_id, "company_id": company_id,
            "batch_reference": f"BATCH-SAMPLE-001",
            "payroll_period": "2026-06",
            "total_records": 7, "ready_count": 3, "review_count": 2, "blocked_count": 2,
            "saudization_ratio": 28.5, "nitaqat_band": "low_green",
            "total_gosi_liability": 8450.00, "penalty_exposure": 35000.00,
            "company_health_score": 62, "engine_version": "0.2.0",
            "rules_version": "2026-06-01", "status": "complete",
        }], use_admin=True)
    except Exception:
        pass

    # Create sample employees (recreate)
    try:
        await delete("employee_records", {"company_id": f"eq.{company_id}"}, use_admin=True)
    except Exception:
        pass

    employees = [
        {"employee_name": "Khalid Al-Ghamdi", "iqama_number": "1098273847", "nationality": "Saudi Arabia", "basic_salary": 14000, "total_gross_wage": 18700, "raw_job_title": "Project Manager", "ssco_code": "2142", "compliance_status": "ready", "flags": []},
        {"employee_name": "Ahmed Al-Harbi", "iqama_number": "2039485761", "nationality": "Saudi Arabia", "basic_salary": 3500, "total_gross_wage": 4500, "raw_job_title": "Procurement Officer", "ssco_code": "3323", "compliance_status": "review", "flags": ["WPS_FLOOR_VIOLATION"]},
        {"employee_name": "Mohammed Al-Qahtani", "iqama_number": "3048572910", "nationality": "Saudi Arabia", "basic_salary": 6000, "total_gross_wage": 7500, "raw_job_title": "Civil Engineer", "ssco_code": "2142", "compliance_status": "review", "flags": ["ENGINEER_WAGE_FLOOR_VIOLATION"]},
        {"employee_name": "Fahad Al-Otaibi", "iqama_number": "4057681920", "nationality": "Saudi Arabia", "basic_salary": 12000, "total_gross_wage": 15500, "raw_job_title": "Architect", "ssco_code": "2141", "compliance_status": "ready", "flags": []},
        {"employee_name": "Nora Al-Shehri", "iqama_number": "5068792031", "nationality": "Saudi Arabia", "basic_salary": 4000, "total_gross_wage": 5000, "raw_job_title": "HR Coordinator", "ssco_code": "1212", "compliance_status": "blocked", "flags": ["GOSI_ENROLLMENT_DATE_MISSING"]},
        {"employee_name": "John Smith", "iqama_number": "6079803142", "nationality": "India", "basic_salary": 3500, "total_gross_wage": 4200, "raw_job_title": "Laborer", "ssco_code": "9333", "compliance_status": "ready", "flags": []},
        {"employee_name": "Ali Hassan", "iqama_number": "7080914253", "nationality": "Egypt", "basic_salary": 3200, "total_gross_wage": 3800, "raw_job_title": "Driver", "ssco_code": "9333", "compliance_status": "blocked", "flags": ["WPS_FLOOR_VIOLATION"]},
    ]

    created = 0
    for emp in employees:
        try:
            await insert("employee_records", [{
                "id": str(uuid.uuid4()), "company_id": company_id, "batch_id": batch_id,
                "ref_id": f"emp-{created+1:04d}", **emp,
            }], use_admin=True)
            created += 1
        except Exception:
            pass

    return {
        "success": True, "employees_created": created,
        "message": f"Seeded {created} employees. Refresh the dashboard.",
    }