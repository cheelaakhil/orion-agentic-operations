"""
Unit tests for Deterministic Anomaly Engine and Evidence Package Builder.
"""

from datetime import datetime
import pytest

from backend.services.analytics.anomalies import (
    AnomalySeverity,
    DeterministicAnomalyEngine,
    anomaly_engine,
)
from backend.services.analytics.evidence import generate_evidence_package


def test_anomaly_detection_engine(populated_db):
    b_start = datetime(2026, 5, 1)
    b_end = datetime(2026, 5, 31)
    e_start = datetime(2026, 6, 1)
    e_end = datetime(2026, 6, 30)

    anomalies = anomaly_engine.detect_all_anomalies(
        db=populated_db,
        baseline_start=b_start,
        baseline_end=b_end,
        evaluation_start=e_start,
        evaluation_end=e_end,
    )

    # We expect:
    # 1. Revenue drop anomaly
    # 2. Support SLA breach rate spike
    # 3. Inventory stockout rate spike
    # 4. Repeat purchase rate drop
    # 5. Order cancellation rate anomaly
    metric_names = [a.metric for a in anomalies]
    assert "daily_revenue" in metric_names
    assert "support_sla_breach_rate" in metric_names
    assert "inventory_stockout_rate" in metric_names
    assert "repeat_purchase_rate" in metric_names
    assert "order_cancellation_rate" in metric_names

    # Check revenue drop severity
    rev_anom = next(a for a in anomalies if a.metric == "daily_revenue")
    assert rev_anom.change_percentage < 0
    assert rev_anom.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]

    # Check support SLA spike severity
    sla_anom = next(a for a in anomalies if a.metric == "support_sla_breach_rate")
    assert sla_anom.current_value > sla_anom.baseline_value
    assert sla_anom.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]


def test_evidence_package_generation(populated_db):
    b_start = datetime(2026, 5, 1)
    b_end = datetime(2026, 5, 31)
    e_start = datetime(2026, 6, 1)
    e_end = datetime(2026, 6, 30)

    anomalies = anomaly_engine.detect_all_anomalies(
        db=populated_db,
        baseline_start=b_start,
        baseline_end=b_end,
        evaluation_start=e_start,
        evaluation_end=e_end,
    )
    rev_anom = next(a for a in anomalies if a.metric == "daily_revenue")

    package = generate_evidence_package(
        db=populated_db,
        anomaly=rev_anom,
        baseline_start=b_start,
        baseline_end=b_end,
        evaluation_start=e_start,
        evaluation_end=e_end,
    )

    # Verify all 5 operational dimensions are quantitatively populated
    assert package.anomaly_id == rev_anom.anomaly_id
    assert package.revenue.baseline_revenue == 345.00
    assert package.revenue.evaluation_revenue == 75.00
    assert "North America" in package.revenue.by_region_baseline

    assert package.support.baseline_ticket_volume == 2
    assert package.support.evaluation_avg_resolution_hours == 30.25
    assert package.support.evaluation_sla_breach_rate == 1.0

    assert package.inventory.baseline_stockout_rate == 0.0
    assert package.inventory.evaluation_stockout_rate == round(1.0 / 3.0, 4)
    assert "Electronics" in package.inventory.stockout_rate_by_category

    assert package.customers.baseline_repeat_purchase_rate > 0.5
    assert package.customers.evaluation_repeat_purchase_rate == 0.0

    assert package.marketing.total_spend == 1000.00
    assert package.marketing.roas == 1.75
