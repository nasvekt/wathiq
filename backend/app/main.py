"""
Wathiq Compliance Gateway — FastAPI Backend
Main application entry point.
"""

__version__ = "0.1.0"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import compliance, health

app = FastAPI(
    title="Wathiq Compliance Gateway",
    description="Saudi corporate payroll compliance validation API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["System"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance"])
