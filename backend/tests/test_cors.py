"""
CORS Configuration Tests for ORION FastAPI Backend.
Verifies preflight and GET requests from the production Vercel frontend origin and localhost.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

PROD_VERCEL_ORIGIN = "https://orion-agentic-operations-4jim19l0i-cheela-akhils-projects.vercel.app"
LOCALHOST_ORIGIN = "http://localhost:3000"


def test_cors_preflight_production_vercel_origin():
    """Verify OPTIONS preflight request from the Vercel production origin succeeds with proper headers."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": PROD_VERCEL_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PROD_VERCEL_ORIGIN


def test_cors_get_production_vercel_origin():
    """Verify GET request from the Vercel production origin returns Access-Control-Allow-Origin."""
    response = client.get(
        "/api/v1/health",
        headers={"Origin": PROD_VERCEL_ORIGIN},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PROD_VERCEL_ORIGIN


def test_cors_get_localhost_origin():
    """Verify local development requests from localhost:3000 are preserved."""
    response = client.get(
        "/api/v1/health",
        headers={"Origin": LOCALHOST_ORIGIN},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == LOCALHOST_ORIGIN


def test_cors_anomalies_production_vercel_origin():
    """Verify /api/v1/anomalies allows access from production Vercel origin."""
    response = client.get(
        "/api/v1/anomalies",
        headers={"Origin": PROD_VERCEL_ORIGIN},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == PROD_VERCEL_ORIGIN
