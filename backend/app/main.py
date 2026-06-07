"""
Wathiq Compliance Gateway — FastAPI Backend
Resilient startup — health endpoint loads first, other routers load lazily.
"""

__version__ = "0.2.0"

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Wathiq Compliance Gateway",
    description="Saudi corporate payroll compliance validation API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health endpoint — imported directly, always works ──
from app.routers.health import router as health_router
app.include_router(health_router, tags=["System"])

# ── All other routers — imported lazily ──
def _include_router(module_path: str, router_attr: str, prefix: str = "", tags: list | None = None):
    """Import and include a router. Silently skip if it fails."""
    try:
        import importlib
        mod = importlib.import_module(module_path)
        router = getattr(mod, router_attr)
        app.include_router(router, prefix=prefix, tags=tags or [])
    except Exception as e:
        import sys
        print(f"[warn] Router {module_path}.{router_attr} failed to load: {e}", file=sys.stderr)

# API v1
_include_router("app.routers.compliance", "router", "/api/v1", ["Compliance"])
_include_router("app.routers.gosi", "router", "/api/v1", ["GOSI"])
_include_router("app.routers.nitaqat", "router", "/api/v1", ["Nitaqat"])
_include_router("app.routers.ingestion", "router", "/api/v1", ["Ingestion"])
_include_router("app.routers.sif_export", "router", "/api/v1", ["SIF Export"])
_include_router("app.routers.procurement", "router", "/api/v1", ["Procurement"])

# Frontend-facing API
_include_router("app.routers.frontend_auth", "router", "/api/auth", ["Frontend Auth"])
_include_router("app.routers.frontend_api", "router", "/api", ["Frontend API"])

# Qiwa Shield
_include_router("app.features.qiwa_shield.router", "router", "/api/v1", ["Qiwa Shield"])

# ── Frontend SPA ──
DASHBOARD_DIST = Path(__file__).resolve().parent.parent.parent / "dashboard" / "dist"
if DASHBOARD_DIST.exists() and (DASHBOARD_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(DASHBOARD_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        index_path = DASHBOARD_DIST / "index.html"
        if index_path.exists():
            return HTMLResponse(content=index_path.read_text())
        return JSONResponse(status_code=404, content={"detail": "Frontend not built"})