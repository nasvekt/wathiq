"""
Wathiq Compliance Gateway — FastAPI Backend
Main application entry point.
"""

__version__ = "0.2.0"

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import compliance, health, gosi, nitaqat, ingestion, sif_export
from app.routers import frontend_auth, frontend_api, procurement

# ── Frontend Paths ──
DASHBOARD_DIST = Path(__file__).resolve().parent.parent.parent / "dashboard" / "dist"

app = FastAPI(
    title="Wathiq Compliance Gateway",
    description="Saudi corporate payroll compliance validation API",
    version="0.2.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers — defined BEFORE the SPA catch-all ──
app.include_router(health.router, tags=["System"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance"])
app.include_router(gosi.router, prefix="/api/v1", tags=["GOSI"])
app.include_router(nitaqat.router, prefix="/api/v1", tags=["Nitaqat"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(sif_export.router, prefix="/api/v1", tags=["SIF Export"])

# ── Frontend-facing endpoints ──
app.include_router(frontend_auth.router, prefix="/api/auth", tags=["Frontend Auth"])
app.include_router(frontend_api.router, prefix="/api", tags=["Frontend API"])
app.include_router(procurement.router, prefix="/api/v1", tags=["Procurement"])

# ── Serve static assets (JS, CSS, images) ──
if DASHBOARD_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(DASHBOARD_DIST / "assets")), name="assets")


    # ── SPA catch-all — serve index.html for all non-API, non-static routes ──
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve the SPA for all routes that aren't API endpoints."""
        # Don't catch API routes
        if full_path.startswith("api/"):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        index_path = DASHBOARD_DIST / "index.html"
        if index_path.exists():
            return HTMLResponse(content=index_path.read_text())
        return JSONResponse(status_code=404, content={"detail": "Frontend not built"})