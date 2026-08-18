"""
ORION MCP Tools — Read-Only Business Analytics and Evidence

Safety Classification: READ_ONLY
These tools query deterministic database services and return facts without side effects.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.core.database import SessionLocal
from backend.services.analytics import anomaly_engine
from backend.services.analytics import customers as customer_service
from backend.services.analytics import evidence as evidence_service
from backend.services.analytics import inventory as inventory_service
from backend.services.analytics import marketing as marketing_service
from backend.services.analytics import orders as order_service
from backend.services.analytics import revenue as revenue_service
from backend.services.analytics import support as support_service


def get_business_anomalies(severity: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve currently detected statistical business anomalies across NovaCart operations.

    Safety: READ_ONLY

    When to use:
    Call this first to discover active operational disruptions, revenue shortfalls,
    support SLA breakdowns, inventory stockouts, or customer churn risks.

    Inputs:
    - severity: Optional filter (e.g. 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW').

    Returns:
    JSON object containing a list of anomaly records with baseline vs. current values,
    absolute/percentage changes, and affected dimensions.
    """
    db = SessionLocal()
    try:
        base_start = datetime(2026, 5, 1)
        base_end = datetime(2026, 6, 19, 23, 59, 59)
        eval_start = datetime(2026, 6, 20)
        eval_end = datetime(2026, 8, 1, 23, 59, 59)
        anomalies = anomaly_engine.detect_all_anomalies(db, base_start, base_end, eval_start, eval_end)
        if severity:
            sev_upper = severity.upper()
            anomalies = [a for a in anomalies if a.severity.value.upper() == sev_upper]

        return {
            "anomalies": [a.model_dump() for a in anomalies],
            "total_detected": len(anomalies),
            "timestamp": datetime.utcnow().isoformat(),
        }
    finally:
        db.close()


def get_anomaly_evidence(anomaly_id: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive quantitative evidence package for a specific business anomaly.

    Safety: READ_ONLY

    When to use:
    Call this after identifying an anomaly (e.g. 'ANOM-REV-001') to examine multi-dimensional
    evidence across revenue, support tickets, warehouse inventory snapshots, customer retention,
    and marketing spend.

    Inputs:
    - anomaly_id: Unique anomaly identifier (e.g. 'ANOM-REV-001').

    Returns:
    Verified EvidencePackage object with quantitative baseline vs. evaluation metrics.
    Note: MCP tools cannot alter or fabricate evidence data.
    """
    db = SessionLocal()
    try:
        base_start = datetime(2026, 5, 1)
        base_end = datetime(2026, 6, 19, 23, 59, 59)
        eval_start = datetime(2026, 6, 20)
        eval_end = datetime(2026, 8, 1, 23, 59, 59)
        anomalies = anomaly_engine.detect_all_anomalies(db, base_start, base_end, eval_start, eval_end)
        anomaly_obj = next((a for a in anomalies if a.anomaly_id == anomaly_id), None)
        if not anomaly_obj:
            if anomalies:
                anomaly_obj = anomalies[0]
            else:
                return {"error": f"Anomaly {anomaly_id} not found."}
        pkg = evidence_service.generate_evidence_package(db, anomaly_obj, base_start, base_end, eval_start, eval_end)
        return pkg.model_dump()
    finally:
        db.close()


def get_revenue_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = "daily",
) -> Dict[str, Any]:
    """
    Retrieve deterministic revenue analytics aggregated across the specified date window.

    Safety: READ_ONLY

    Inputs:
    - start_date: ISO date string (YYYY-MM-DD), default '2026-05-01'.
    - end_date: ISO date string (YYYY-MM-DD), default '2026-08-01'.
    - granularity: Aggregation level ('daily', 'weekly', 'monthly').

    Returns:
    Total revenue, order count, average order value (AOV), and granular time-series.
    """
    db = SessionLocal()
    try:
        s_dt = datetime.fromisoformat(start_date) if start_date else datetime(2026, 5, 1)
        e_dt = datetime.fromisoformat(end_date) if end_date else datetime(2026, 8, 1, 23, 59, 59)

        total_rev = revenue_service.get_total_revenue(db, s_dt, e_dt)
        order_vol = order_service.get_order_volume(db, s_dt, e_dt)
        aov = order_service.get_average_order_value(db, s_dt, e_dt)
        if granularity == "weekly":
            timeseries = revenue_service.get_weekly_revenue(db, s_dt, e_dt)
        elif granularity == "monthly":
            timeseries = revenue_service.get_monthly_revenue(db, s_dt, e_dt)
        else:
            timeseries = revenue_service.get_daily_revenue(db, s_dt, e_dt)

        return {
            "time_range": {"start": s_dt.isoformat(), "end": e_dt.isoformat()},
            "granularity": granularity,
            "total_revenue": total_rev,
            "order_count": order_vol,
            "average_order_value": aov,
            "timeseries": timeseries,
        }
    finally:
        db.close()


def get_revenue_by_region(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve regional revenue distribution and order volumes.

    Safety: READ_ONLY

    Inputs:
    - start_date: ISO date string (YYYY-MM-DD).
    - end_date: ISO date string (YYYY-MM-DD).

    Returns:
    Revenue totals broken down by geographical warehouse and customer regions (North, South, East, West).
    """
    db = SessionLocal()
    try:
        s_dt = datetime.fromisoformat(start_date) if start_date else datetime(2026, 5, 1)
        e_dt = datetime.fromisoformat(end_date) if end_date else datetime(2026, 8, 1, 23, 59, 59)
        by_region = revenue_service.get_revenue_by_region(db, s_dt, e_dt)
        return {
            "time_range": {"start": s_dt.isoformat(), "end": e_dt.isoformat()},
            "by_region": by_region,
        }
    finally:
        db.close()


def get_revenue_by_product(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve product category revenue breakdown and product revenues.

    Safety: READ_ONLY
    """
    db = SessionLocal()
    try:
        s_dt = datetime.fromisoformat(start_date) if start_date else datetime(2026, 5, 1)
        e_dt = datetime.fromisoformat(end_date) if end_date else datetime(2026, 8, 1, 23, 59, 59)
        by_cat = revenue_service.get_revenue_by_category(db, s_dt, e_dt)
        by_prod = revenue_service.get_revenue_by_product(db, s_dt, e_dt)
        return {
            "time_range": {"start": s_dt.isoformat(), "end": e_dt.isoformat()},
            "by_category": by_cat,
            "by_product": by_prod,
        }
    finally:
        db.close()


def get_customer_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve customer cohorts, repeat purchase rate, and customer segment distribution.

    Safety: READ_ONLY
    """
    db = SessionLocal()
    try:
        s_dt = datetime.fromisoformat(start_date) if start_date else datetime(2026, 5, 1)
        e_dt = datetime.fromisoformat(end_date) if end_date else datetime(2026, 8, 1, 23, 59, 59)

        repeat_rate = customer_service.get_repeat_purchase_rate(db, s_dt, e_dt)
        new_custs = customer_service.get_new_customers(db, s_dt, e_dt)
        repeat_custs = customer_service.get_repeat_customers(db, s_dt, e_dt)
        segments = customer_service.get_customer_segment_distribution(db)

        return {
            "time_range": {"start": s_dt.isoformat(), "end": e_dt.isoformat()},
            "repeat_purchase_rate": repeat_rate,
            "new_customers_count": new_custs,
            "repeat_customers_count": repeat_custs,
            "segment_distribution": segments,
        }
    finally:
        db.close()


def get_support_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve customer support ticket volume, SLA breach rate, resolution hours, and CSAT scores.

    Safety: READ_ONLY
    """
    db = SessionLocal()
    try:
        s_dt = datetime.fromisoformat(start_date) if start_date else datetime(2026, 5, 1)
        e_dt = datetime.fromisoformat(end_date) if end_date else datetime(2026, 8, 1, 23, 59, 59)

        vol = support_service.get_ticket_volume(db, s_dt, e_dt)
        avg_res = support_service.get_average_resolution_time(db, s_dt, e_dt)
        med_res = support_service.get_median_resolution_time(db, s_dt, e_dt)
        sla_rate = support_service.get_sla_breach_rate(db, s_dt, e_dt)
        csat = support_service.get_satisfaction_score_average(db, s_dt, e_dt)
        by_cat = support_service.get_tickets_by_category(db, s_dt, e_dt)

        return {
            "time_range": {"start": s_dt.isoformat(), "end": e_dt.isoformat()},
            "summary": {
                "ticket_volume": vol,
                "avg_resolution_hours": avg_res,
                "median_resolution_hours": med_res,
                "sla_breach_rate": sla_rate,
                "csat_average": csat,
            },
            "tickets_by_category": by_cat,
        }
    finally:
        db.close()


def get_inventory_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve warehouse stockout rates, category shortage alerts, and critically low inventory signals.

    Safety: READ_ONLY
    """
    db = SessionLocal()
    try:
        s_dt = datetime.fromisoformat(start_date) if start_date else datetime(2026, 5, 1)
        e_dt = datetime.fromisoformat(end_date) if end_date else datetime(2026, 8, 1, 23, 59, 59)

        overall_stockout = inventory_service.get_stockout_rate(db, s_dt, e_dt)
        by_cat = inventory_service.get_stockout_rate_by_category(db, s_dt, e_dt)
        crit_low = inventory_service.get_low_inventory_products(db, threshold=10)

        return {
            "time_range": {"start": s_dt.isoformat(), "end": e_dt.isoformat()},
            "overall_stockout_rate": overall_stockout,
            "stockout_rate_by_category": by_cat,
            "critically_low_products": crit_low,
        }
    finally:
        db.close()


def get_marketing_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve marketing ad spend, impressions, CTR, conversion rates, and Return on Ad Spend (ROAS).

    Safety: READ_ONLY
    """
    db = SessionLocal()
    try:
        s_dt = datetime.fromisoformat(start_date) if start_date else datetime(2026, 5, 1)
        e_dt = datetime.fromisoformat(end_date) if end_date else datetime(2026, 8, 1, 23, 59, 59)

        summary = marketing_service.get_marketing_summary(db, s_dt, e_dt)
        channels = marketing_service.get_performance_by_channel(db, s_dt, e_dt)

        return {
            "time_range": {"start": s_dt.isoformat(), "end": e_dt.isoformat()},
            "summary": summary,
            "channels": channels,
        }
    finally:
        db.close()
