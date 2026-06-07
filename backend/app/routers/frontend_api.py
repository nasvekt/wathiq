"""
Wathiq — Frontend-facing API endpoints with Supabase integration.
Queries real data from Supabase, falls back to mock when empty.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.database import select, insert, update
from datetime import date

router = APIRouter()

MOCK_COMPANY_ID = "dev-company-001"


async def _get_or_seed(table: str, default_data: list[dict], params: dict | None = None) -> list[dict]:
    """Try Supabase first, seed if empty, fall back to mock on error."""
    try:
        result = await select(table, params)
        if result:
            return result
        # Seed with default data
        if default_data:
            await insert(table, default_data)
        return default_data
    except Exception:
        return default_data


@router.get("/compliance/dashboard")
async def dashboard():
    """Get dashboard summary from Supabase or mock."""
    # Try to get latest audit batch
    try:
        batches = await select("audit_batches", {
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
            "at_risk_count": 5,
            "pending_count": 0,
            "penalty_exposure": float(b.get("penalty_exposure", 0)) if b.get("penalty_exposure") else 65000,
            "total_gosi_liability": float(b.get("total_gosi_liability", 0)) if b.get("total_gosi_liability") else 18450,
            "iqama_expiring_soon": 5,
            "last_audit_date": str(b.get("created_at", ""))[:10] if b.get("created_at") else "2026-06-01",
            "source": "supabase",
        }

    # No data yet — return mock
    return {
        "health_score": 74,
        "health_score_trend": "down",
        "nitaqat_band": "low_green",
        "nitaqat_percentage": 28.5,
        "total_employees": 150,
        "ready_count": 120,
        "review_count": 20,
        "blocked_count": 10,
        "at_risk_count": 5,
        "pending_count": 15,
        "penalty_exposure": 65000.00,
        "total_gosi_liability": 18450.00,
        "iqama_expiring_soon": 5,
        "last_audit_date": "2026-06-01",
        "source": "mock",
    }


@router.get("/compliance/employees")
async def employees(
    search: Optional[str] = None,
    status: Optional[str] = None,
    nationality: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """Get employees from Supabase or return samples."""
    try:
        params = {"limit": str(page_size), "offset": str((page - 1) * page_size)}
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
            "basic_salary": float(r.get("basic_salary", 0)) if r.get("basic_salary") else 0,
            "housing_allowance": float(r.get("housing_allowance", 0)) if r.get("housing_allowance") else 0,
            "gross_salary": float(r.get("total_gross_wage", 0)) if r.get("total_gross_wage") else 0,
            "status": r.get("compliance_status", "pending"),
            "flags": r.get("flags", []) or [],
        } for r in results]
        return {"total": len(mapped), "page": page, "page_size": page_size, "results": mapped}

    # Mock fallback
    return _mock_employees(search, status, page, page_size)


@router.get("/compliance/health-score")
async def health_score():
    """Get health score breakdown."""
    return {
        "score": 74, "previous_score": 82, "change": -8, "trend": "down",
        "breakdown": {"gosi": 18, "wps": 15, "nitaqat": 12, "iqama": 10, "contracts": 19},
    }


@router.get("/compliance/iqama-calendar")
async def iqama_calendar():
    """Get Iqama expiry tracking."""
    return {
        "total_active": 120, "expiring_90_days": 8, "expiring_60_days": 3,
        "expiring_30_days": 2, "expired": 1,
        "upcoming": [
            {"employee": "John Smith", "iqama": "2039485761", "expiry": "2026-07-15", "days_left": 40},
            {"employee": "Ali Hassan", "iqama": "3048572910", "expiry": "2026-06-20", "days_left": 15},
            {"employee": "Sara Ahmed", "iqama": "4057681920", "expiry": "2026-06-10", "days_left": 5},
        ],
    }


@router.get("/compliance/contracts")
async def contract_tracker():
    """Get Qiwa contract window tracking."""
    return {
        "total_pending": 3, "warning_next_5_days": 2, "violations": 1,
        "upcoming": [
            {"employee": "Fahad Al-Otaibi", "hire_date": "2026-05-10", "deadline": "2026-06-09", "days_left": 4, "status": "warning"},
            {"employee": "Nora Al-Shehri", "hire_date": "2026-05-05", "deadline": "2026-06-04", "days_left": -1, "status": "violation"},
        ],
    }


@router.get("/compliance/trends")
async def compliance_trends(range: Optional[str] = "6m"):
    """Get compliance trend data."""
    return {
        "health_score": [
            {"month": "2026-01", "score": 85}, {"month": "2026-02", "score": 82},
            {"month": "2026-03", "score": 79}, {"month": "2026-04", "score": 76},
            {"month": "2026-05", "score": 74},
        ],
        "saudization": [
            {"month": "2026-01", "ratio": 32.0}, {"month": "2026-02", "ratio": 31.5},
            {"month": "2026-03", "ratio": 30.2}, {"month": "2026-04", "ratio": 29.0},
            {"month": "2026-05", "ratio": 28.5},
        ],
        "gosi_liability": [
            {"month": "2026-01", "amount": 17200}, {"month": "2026-02", "amount": 17500},
            {"month": "2026-03", "amount": 17800}, {"month": "2026-04", "amount": 18100},
            {"month": "2026-05", "amount": 18450},
        ],
    }


@router.post("/simulator/nitaqat")
async def simulate_nitaqat():
    return {"current_ratio": 28.5, "current_band": "low_green", "projected_ratio": 35.0, "projected_band": "high_green", "band_drop_warning": False}


@router.get("/wage-sync/batches")
async def wage_batches():
    return {"batches": [
        {"id": "batch-001", "period": "2026-05", "status": "complete", "records": 150, "created": "2026-05-26"},
        {"id": "batch-002", "period": "2026-04", "status": "complete", "records": 148, "created": "2026-04-26"},
    ]}


@router.post("/wage-sync/export")
async def export_sif():
    return {"success": True, "sif_content": "H,1220038481,SA102...", "sha256_hash": "e3b0c44298fc1c14..."}


@router.get("/developer/keys")
async def get_api_keys():
    return {"keys": [{"id": "key-001", "prefix": "wath_ab12", "name": "Production", "created": "2026-05-01", "last_used": "2026-05-26", "active": True}]}


@router.post("/developer/keys")
async def create_api_key(name: str = "Default"):
    return {"key": f"wath_dev_test", "prefix": "wath_dev", "name": name}


@router.delete("/developer/keys/{key_id}")
async def revoke_api_key(key_id: str):
    return {"success": True, "key_id": key_id}


@router.get("/billing")
async def billing_info():
    return {"plan": "professional", "status": "active", "amount": 42000, "currency": "SAR", "billing_cycle": "annual", "next_billing": "2027-06-01"}


@router.get("/billing/invoices")
async def billing_invoices():
    return {"invoices": [{"id": "inv-001", "date": "2026-06-01", "amount": 42000, "status": "paid"}, {"id": "inv-002", "date": "2026-05-01", "amount": 3500, "status": "paid"}]}


@router.get("/founder/summary")
async def founder_summary():
    return {
        "total_companies": 18, "mrr": 42500, "arr": 510000, "records_processed": 28400,
        "companies_by_tier": {"standard": 8, "professional": 6, "enterprise": 2, "developer": 2},
        "health_distribution": {"green": 12, "yellow": 4, "red": 2},
        "pending_rule_updates": 3,
        "system_health": {"api_latency_ms": 145, "error_rate_pct": 0.02, "queue_depth": 5},
    }


@router.get("/founder/users")
async def founder_users():
    return {"users": [
        {"id": "usr-001", "email": "admin@example.com", "company": "Wathiq Tech", "plan": "enterprise", "status": "active"},
        {"id": "usr-002", "email": "hr@constructco.sa", "company": "ConstructCo", "plan": "professional", "status": "active"},
    ]}


@router.post("/seed/sample-data")
@router.get("/seed/sample-data")
async def seed_sample_data():
    """Seed Supabase with sample company + employee data for testing."""
    import uuid
    from datetime import datetime, timedelta
    from decimal import Decimal

    company_id = "dev-company-001"
    batch_id = str(uuid.uuid4())

    # Create company
    try:
        existing = await select("companies", {"id": f"eq.{company_id}"}, use_admin=True)
        if not existing:
            await insert("companies", [{
                "id": company_id,
                "name": "ConstructCo Saudi Arabia",
                "name_ar": "شركة كونستركتكو السعودية",
                "commercial_registration": "CR-10101010",
                "email": "hr@constructco.sa",
                "economic_sector_code": "construction",
                "establishment_size_category": "medium_a",
                "total_headcount": 150,
                "plan_tier": "professional",
                "is_active": True,
                "onboarding_complete": True,
            }], use_admin=True)
    except Exception:
        pass

    # Create audit batch
    try:
        await insert("audit_batches", [{
            "id": batch_id,
            "company_id": company_id,
            "batch_reference": f"BATCH-{datetime.utcnow().strftime('%Y%m')}-001",
            "payroll_period": datetime.utcnow().strftime("%Y-%m"),
            "total_records": 150,
            "ready_count": 120,
            "review_count": 20,
            "blocked_count": 10,
            "saudization_ratio": 28.5,
            "nitaqat_band": "low_green",
            "total_gosi_liability": 18450.00,
            "penalty_exposure": 65000.00,
            "company_health_score": 74,
            "engine_version": "0.2.0",
            "rules_version": datetime.utcnow().strftime("%Y-%m-%d"),
            "status": "complete",
        }], use_admin=True)
    except Exception:
        pass

    # Create sample employees
    employees = [
        {"employee_name": "Khalid Al-Ghamdi", "iqama_number": "1098273847", "nationality": "Saudi Arabia", "basic_salary": 14000, "total_gross_wage": 18700, "raw_job_title": "Project Manager", "ssco_code": "2142", "compliance_status": "ready", "gosi_enrolled": True},
        {"employee_name": "Ahmed Al-Harbi", "iqama_number": "2039485761", "nationality": "Saudi Arabia", "basic_salary": 3500, "total_gross_wage": 4500, "raw_job_title": "Procurement Officer", "ssco_code": "3323", "compliance_status": "review", "gosi_enrolled": True},
        {"employee_name": "Mohammed Al-Qahtani", "iqama_number": "3048572910", "nationality": "Saudi Arabia", "basic_salary": 6000, "total_gross_wage": 7500, "raw_job_title": "Civil Engineer", "ssco_code": "2142", "compliance_status": "review", "gosi_enrolled": True},
        {"employee_name": "Fahad Al-Otaibi", "iqama_number": "4057681920", "nationality": "Saudi Arabia", "basic_salary": 12000, "total_gross_wage": 15500, "raw_job_title": "Architect", "ssco_code": "2141", "compliance_status": "ready", "gosi_enrolled": True},
        {"employee_name": "Nora Al-Shehri", "iqama_number": "5068792031", "nationality": "Saudi Arabia", "basic_salary": 4000, "total_gross_wage": 5000, "raw_job_title": "HR Coordinator", "ssco_code": "1212", "compliance_status": "ready", "gosi_enrolled": False},
        {"employee_name": "John Smith", "iqama_number": "6079803142", "nationality": "India", "basic_salary": 3500, "total_gross_wage": 4200, "raw_job_title": "Laborer", "ssco_code": "9333", "compliance_status": "ready", "gosi_enrolled": True},
        {"employee_name": "Ali Hassan", "iqama_number": "7080914253", "nationality": "Egypt", "basic_salary": 3200, "total_gross_wage": 3800, "raw_job_title": "Driver", "ssco_code": "9333", "compliance_status": "ready", "gosi_enrolled": True},
    ]

    # Create sample employees (always re-create for fresh seed)
    try:
        # Delete existing employees for this company
        await delete("employee_records", {"company_id": f"eq.{company_id}"}, use_admin=True)
    except Exception:
        pass

    created = 0
    for emp in employees:
        try:
            await insert("employee_records", [{
                "id": str(uuid.uuid4()),
                "company_id": company_id,
                "batch_id": batch_id,
                "ref_id": f"emp-{created+1:04d}",
                **emp,
                "flags": [],
            }], use_admin=True)
            created += 1
        except Exception:
            pass

    return {
        "success": True,
        "company_created": True,
        "batch_created": True,
        "employees_created": created,
        "message": f"Seeded {created} employees for ConstructCo. Refresh the dashboard to see real data.",
    }


# ── Private helpers ──

def _mock_employees(search, status, nationality, page, page_size):
    sample = [
        {"id": "emp-001", "iqama": "1098273847", "name_en": "Khalid Al-Ghamdi", "name_ar": "خالد الغامدي", "nationality": "Saudi Arabia", "job_title": "Lead Ethical Hacker", "ssco_code": "251214", "basic_salary": 14000, "housing_allowance": 3500, "gross_salary": 18700, "status": "ready", "flags": []},
        {"id": "emp-002", "iqama": "2039485761", "name_en": "Ahmed Al-Harbi", "name_ar": "أحمد الحربي", "nationality": "Saudi Arabia", "job_title": "Procurement Officer", "ssco_code": "3323", "basic_salary": 3500, "housing_allowance": 1000, "gross_salary": 4500, "status": "review", "flags": ["WPS_FLOOR_VIOLATION"]},
        {"id": "emp-003", "iqama": "3048572910", "name_en": "Mohammed Al-Qahtani", "name_ar": "محمد القحطاني", "nationality": "Saudi Arabia", "job_title": "Civil Engineer", "ssco_code": "2142", "basic_salary": 6000, "housing_allowance": 1500, "gross_salary": 7500, "status": "review", "flags": ["ENGINEER_WAGE_FLOOR_VIOLATION"]},
        {"id": "emp-004", "iqama": "1059483019", "name_en": "Mohammed Alsubaie", "name_ar": "محمد السبيعي", "nationality": "Saudi Arabia", "job_title": "Software Developer", "ssco_code": "2512", "basic_salary": 12000, "housing_allowance": 3000, "gross_salary": 15500, "status": "ready", "flags": []},
    ]
    filtered = [e for e in sample if not status or e["status"] == status]
    return {"total": len(filtered), "page": page, "page_size": page_size, "results": filtered}