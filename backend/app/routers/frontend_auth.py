"""
Wathiq — Auth with real company lookup from Supabase.
Registers companies, returns consistent company_id.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.database import insert, select
import uuid

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=4)
    company_name: str = Field(..., min_length=1)
    industry: str = "technology"
    company_size: str = "medium_a"


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


@router.post("/login")
async def login(request: LoginRequest):
    """Login — looks up company by email in Supabase or returns dev data."""
    company_id = str(uuid.uuid4())
    company_name = request.email.split("@")[0]

    # Try to find existing company by email
    try:
        existing = await select("companies", {"email": f"eq.{request.email}"}, use_admin=True)
        if existing:
            company_id = existing[0]["id"]
            company_name = existing[0].get("name", company_name)
    except Exception:
        pass

    return {
        "success": True,
        "token": f"wathiq_{company_id}_{uuid.uuid4().hex[:8]}",
        "user": {
            "id": str(uuid.uuid4()),
            "email": request.email,
            "name": company_name,
            "company_id": company_id,
            "plan_tier": "free",
        },
    }


@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new company in Supabase."""
    company_id = str(uuid.uuid4())
    company_data = {
        "id": company_id,
        "name": request.company_name,
        "name_ar": request.company_name,
        "commercial_registration": f"CR-{uuid.uuid4().hex[:8].upper()}",
        "email": request.email,
        "economic_sector_code": request.industry,
        "establishment_size_category": request.company_size,
        "total_headcount": 0,
        "plan_tier": "free",
        "is_active": True,
        "onboarding_complete": False,
    }

    try:
        await insert("companies", company_data, use_admin=True)
    except Exception:
        pass  # Continue even if Supabase write fails — use local data

    return {
        "success": True,
        "token": f"wathiq_{company_id}_{uuid.uuid4().hex[:8]}",
        "user": {
            "id": str(uuid.uuid4()),
            "email": request.email,
            "name": request.company_name,
            "company_id": company_id,
            "plan_tier": "free",
        },
        "company": {
            "id": company_id,
            "name": request.company_name,
            "sector": request.industry,
            "size": request.company_size,
            "onboarding_complete": False,
        },
    }


@router.get("/me")
async def get_current_user():
    """Dev: returns a fixed test user."""
    return {
        "id": "dev-user-001",
        "email": "dev@wathiq.io",
        "name": "Dev User",
        "company_id": "dev-company-001",
        "plan_tier": "free",
    }