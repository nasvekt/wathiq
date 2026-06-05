"""
Wathiq Compliance Gateway — FastAPI Backend
Main application entry point.
"""

__version__ = "0.2.0"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import compliance, health, gosi, nitaqat, ingestion, sif_export

app = FastAPI(
    title="Wathiq Compliance Gateway",
    description="Saudi corporate payroll compliance validation API",
    version="0.2.0",
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
app.include_router(gosi.router, prefix="/api/v1", tags=["GOSI"])
app.include_router(nitaqat.router, prefix="/api/v1", tags=["Nitaqat"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(sif_export.router, prefix="/api/v1", tags=["SIF Export"])