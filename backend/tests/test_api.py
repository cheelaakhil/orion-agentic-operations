"""
Tests for FastAPI REST endpoints using Starlette/FastAPI TestClient.
"""

from fastapi.testclient import TestClient
import pytest

from backend.core.database import get_db
from backend.main import app


@pytest.fixture
def client(populated_db):
    """Override get_db dependency with test database session."""
    def _get_test_db():
        yield populated_db

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "orion-backend"


def test_analytics_revenue_endpoint(client):
    res = client.get("/api/v1/analytics/revenue?start_date=2026-05-01&end_date=2026-05-31")
    assert res.status_code == 200
    data = res.json()
    assert data["total_revenue"] == 345.00
    assert len(data["time_series"]) == 5


def test_analytics_regions_and_products_endpoints(client):
    reg_res = client.get("/api/v1/analytics/revenue/regions?start_date=2026-05-01&end_date=2026-05-31")
    assert reg_res.status_code == 200
    assert "North America" in reg_res.json()["regions"]

    prod_res = client.get("/api/v1/analytics/revenue/products?start_date=2026-05-01&end_date=2026-05-31")
    assert prod_res.status_code == 200
    assert len(prod_res.json()["products"]) >= 1


def test_analytics_customers_endpoint(client):
    res = client.get("/api/v1/analytics/customers?start_date=2026-05-01&end_date=2026-05-31")
    assert res.status_code == 200
    data = res.json()
    assert data["total_customers"] == 3
    assert data["repeat_customers"] == 2


def test_analytics_support_endpoint(client):
    res = client.get("/api/v1/analytics/support?start_date=2026-06-01&end_date=2026-06-30")
    assert res.status_code == 200
    data = res.json()
    assert data["total_tickets"] == 2
    assert data["sla_breach_rate"] == 1.0


def test_analytics_inventory_endpoint(client):
    res = client.get("/api/v1/analytics/inventory?start_date=2026-06-01&end_date=2026-06-30")
    assert res.status_code == 200
    data = res.json()
    assert data["overall_stockout_rate"] > 0


def test_analytics_marketing_endpoint(client):
    res = client.get("/api/v1/analytics/marketing?start_date=2026-05-01&end_date=2026-05-31")
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["total_spend"] == 1000.00


def test_anomalies_and_evidence_endpoints(client):
    anom_res = client.get("/api/v1/anomalies?baseline_start=2026-05-01&baseline_end=2026-05-31&eval_start=2026-06-01&eval_end=2026-06-30")
    assert anom_res.status_code == 200
    anomalies = anom_res.json()
    assert len(anomalies) >= 3

    rev_id = anomalies[0]["anomaly_id"]
    ev_res = client.get(f"/api/v1/anomalies/{rev_id}/evidence?baseline_start=2026-05-01&baseline_end=2026-05-31&eval_start=2026-06-01&eval_end=2026-06-30")
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    assert ev_data["anomaly_id"] == rev_id
    assert "revenue" in ev_data
    assert "support" in ev_data
    assert "inventory" in ev_data
    assert "customers" in ev_data
    assert "marketing" in ev_data
