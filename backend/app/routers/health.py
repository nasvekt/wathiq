"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "wathiq-compliance-gateway", "version": "0.1.0"}


@router.get("/api/v1/health")
async def health_check_v1():
    return {"status": "ok", "service": "wathiq-compliance-gateway", "version": "0.1.0"}


@router.get("/")
async def root():
    return {"status": "ok", "service": "wathiq-compliance-gateway", "version": "0.1.0"}
