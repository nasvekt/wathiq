"""
Wathiq — Auth endpoints for frontend login/register.
Development-mode auth — returns mock tokens.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid

router = APIRouter()


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=4)
    company_name: str = Field(..., min_length=1)
    industry: str = Field(default="technology")
    company_size: str = Field(default="medium_a")


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate user. Returns JWT token and user profile."""
    return {
        "success": True,
        "token": f"wathiq_dev_token_{uuid.uuid4().hex}",
        "user": {
            "id": str(uuid.uuid4()),
            "email": request.email,
            "name": request.email.split("@")[0],
            "company_id": str(uuid.uuid4()),
            "plan_tier": "professional",
        },
    }


@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new company account."""
    return {
        "success": True,
        "token": f"wathiq_dev_token_{uuid.uuid4().hex}",
        "user": {
            "id": str(uuid.uuid4()),
            "email": request.email,
            "name": request.company_name,
            "company_id": str(uuid.uuid4()),
            "plan_tier": "standard",
        },
        "company": {
            "id": str(uuid.uuid4()),
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
        "plan_tier": "professional",
    }