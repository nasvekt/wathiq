"""Health check endpoint."""
from fastapi import APIRouter
from app.config import get_settings

router = APIRouter()

HEALTH_CACHE = {}


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "wathiq-compliance-gateway", "version": "0.1.0"}


@router.get("/api/v1/health")
async def health_check_v1():
    return {"status": "ok", "service": "wathiq-compliance-gateway", "version": "0.1.0"}


@router.get("/")
async def root():
    return {"status": "ok", "service": "wathiq-compliance-gateway", "version": "0.1.0"}


@router.get("/debug/env")
async def debug_env():
    """Diagnostic: check if Supabase env vars are loaded. NEVER expose in production."""
    s = get_settings()
    return {
        "supabase_url_set": bool(s.supabase_url),
        "supabase_key_set": bool(s.supabase_key),
        "supabase_key_length": len(s.supabase_key) if s.supabase_key else 0,
        "supabase_service_role_key_set": bool(s.supabase_service_role_key),
        "supabase_service_role_key_length": len(s.supabase_service_role_key) if s.supabase_service_role_key else 0,
    }
