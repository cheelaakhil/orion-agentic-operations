"""
ORION Backend — FastAPI Application Entry Point

Provides REST API for:
- Deterministic analytics across operations
- Anomaly detection & multi-dimensional evidence packages
- Operational health checks
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.actions import router as actions_router
from backend.api.agent_run import router as agent_run_router
from backend.api.analytics import router as analytics_router
from backend.api.anomalies import router as anomalies_router
from backend.api.audit import router as audit_router
from backend.api.investigations import router as investigations_router
from backend.api.recommendations import router as recommendations_router
from backend.core.config import settings
from backend.core.database import init_db_if_needed


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    # Initialize schema & seed NovaCart demo dataset if database is unpopulated (for cloud deployments like Render)
    try:
        init_db_if_needed()
    except Exception as e:
        print(f"[WARN] Database initialization warning on startup: {e}")
    yield


app = FastAPI(
    title="ORION API",
    description="AI Business Operations Intelligence System — Multi-Agent Investigation & Governance Pipeline",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS for frontend production and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(anomalies_router, prefix="/api/v1")
app.include_router(investigations_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(actions_router, prefix="/api/v1")
app.include_router(agent_run_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root landing endpoint with interactive documentation and endpoint catalogue."""
    return {
        "system": "ORION — AI Business Operations Intelligence System",
        "version": "0.3.0",
        "status": "operational",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "endpoints": {
            "health": "/api/v1/health",
            "anomalies": "/api/v1/anomalies",
            "evidence_example": "/api/v1/anomalies/ANOM-REV-001/evidence",
            "investigations": "/api/v1/investigations",
            "recommendations": "/api/v1/investigations/{investigation_id}/recommendations",
            "approval_approve": "/api/v1/recommendations/{recommendation_id}/approve",
            "approval_reject": "/api/v1/recommendations/{recommendation_id}/reject",
            "action_execute": "/api/v1/actions/{action_id}/execute",
            "audit_trail": "/api/v1/audit",
            "revenue_analytics": "/api/v1/analytics/revenue",
            "revenue_by_region": "/api/v1/analytics/revenue/regions",
            "revenue_by_product": "/api/v1/analytics/revenue/products",
            "customer_analytics": "/api/v1/analytics/customers",
            "support_analytics": "/api/v1/analytics/support",
            "inventory_analytics": "/api/v1/analytics/inventory",
            "marketing_analytics": "/api/v1/analytics/marketing",
        },
    }


@app.get("/api/v1/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "orion-backend",
        "version": settings.app_version,
    }
