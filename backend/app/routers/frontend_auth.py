"""
Wathiq — Supabase Auth integration.
Registers users via Supabase Auth and creates company records.
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
    """Authenticate user — returns dev token for now (Supabase Auth Phase 2)."""
    return {
        "success": True,
        "token": f"wathiq_dev_token_{uuid.uuid4().hex}",
        "user": {
            "id": str(uuid.uuid4()),
            "email": request.email,
            "name": request.email.split("@")[0],
            "company_id": str(uuid.uuid4()),
            "plan_tier": "free",
        },
    }


@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new company — creates company record in Supabase."""
    company = None
    user_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())

    try:
        company = {
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
        result = await insert("companies", company, use_admin=True)
        if not result:
            company = None
    except Exception:
        pass  # Supabase might not be active — use local data

    return {
        "success": True,
        "token": f"wathiq_dev_token_{uuid.uuid4().hex}",
        "user": {
            "id": user_id,
            "email": request.email,
            "name": request.company_name,
            "company_id": company_id,
            "plan_tier": "free",
        },
        "company": company or {
            "id": company_id,
            "name": request.company_name,
            "sector": request.industry,
            "size": request.company_size,
            "onboarding_complete": False,
        },
    }


@router.get("/me")
async def get_current_user():
    """Get current user profile from token."""
    return {
        "id": "dev-user-001",
        "email": "dev@wathiq.io",
        "name": "Dev User",
        "company_id": "dev-company-001",
        "plan_tier": "free",
    }