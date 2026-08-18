"""
ORION Analytics API Router

REST endpoints for deterministic business intelligence queries.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.analytics import (
    get_average_order_value,
    get_cancellation_rate,
    get_customer_revenue_stats,
    get_customer_segment_distribution,
    get_daily_revenue,
    get_inventory_availability,
    get_low_inventory_products,
    get_marketing_summary,
    get_monthly_revenue,
    get_new_customers,
    get_order_status_distribution,
    get_order_volume,
    get_performance_by_channel,
    get_repeat_customers,
    get_repeat_purchase_rate,
    get_revenue_by_category,
    get_revenue_by_customer_segment,
    get_revenue_by_product,
    get_revenue_by_region,
    get_satisfaction_score_average,
    get_sla_breach_rate,
    get_stockout_rate,
    get_stockout_rate_by_category,
    get_tickets_by_category,
    get_tickets_by_region,
    get_ticket_volume,
    get_total_customers,
    get_total_revenue,
    get_units_sold,
    get_weekly_revenue,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def parse_date(d_str: str | None) -> datetime | None:
    if not d_str:
        return None
    return datetime.fromisoformat(d_str)


@router.get("/revenue")
def get_revenue_analytics(
    start_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
    end_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
    granularity: str = Query("daily", enum=["daily", "weekly", "monthly"]),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve total and time-series revenue."""
    s_dt = parse_date(start_date)
    e_dt = parse_date(end_date)

    tot = get_total_revenue(db, s_dt, e_dt)

    if granularity == "weekly":
        ts = get_weekly_revenue(db, s_dt, e_dt)
    elif granularity == "monthly":
        ts = get_monthly_revenue(db, s_dt, e_dt)
    else:
        ts = get_daily_revenue(db, s_dt, e_dt)

    return {
        "total_revenue": round(tot, 2),
        "granularity": granularity,
        "time_series": ts,
    }


@router.get("/revenue/regions")
def get_revenue_regions(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve revenue distribution by geographic region."""
    s_dt = parse_date(start_date)
    e_dt = parse_date(end_date)
    return {"regions": get_revenue_by_region(db, s_dt, e_dt)}


@router.get("/revenue/products")
def get_revenue_products(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve revenue by product ranking and category totals."""
    s_dt = parse_date(start_date)
    e_dt = parse_date(end_date)
    prods = get_revenue_by_product(db, s_dt, e_dt, limit=limit)
    cats = get_revenue_by_category(db, s_dt, e_dt)
    return {"products": prods, "categories": cats}


@router.get("/customers")
def get_customer_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve customer acquisition, repeat purchase rates, and segment distribution."""
    s_dt = parse_date(start_date) or datetime(2026, 1, 1)
    e_dt = parse_date(end_date) or datetime(2026, 12, 31)

    tot = get_total_customers(db, e_dt)
    new_c = get_new_customers(db, s_dt, e_dt)
    rep_c = get_repeat_customers(db, s_dt, e_dt)
    rep_rate = get_repeat_purchase_rate(db, s_dt, e_dt)
    rev_stats = get_customer_revenue_stats(db, s_dt, e_dt)
    seg_dist = get_customer_segment_distribution(db)
    seg_rev = get_revenue_by_customer_segment(db, s_dt, e_dt)

    return {
        "total_customers": tot,
        "new_customers": new_c,
        "repeat_customers": rep_c,
        "repeat_purchase_rate": rep_rate,
        "revenue_per_customer": rev_stats,
        "segment_distribution": seg_dist,
        "revenue_by_segment": seg_rev,
    }


@router.get("/support")
def get_support_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    region: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve support volume, resolution duration, and SLA breach rate."""
    s_dt = parse_date(start_date)
    e_dt = parse_date(end_date)

    vol = get_ticket_volume(db, s_dt, e_dt, region=region)
    avg_res = get_sla_breach_rate(db, s_dt, e_dt, region=region)
    sla_breach = get_sla_breach_rate(db, s_dt, e_dt, region=region)
    cats = get_tickets_by_category(db, s_dt, e_dt)
    regs = get_tickets_by_region(db, s_dt, e_dt)
    csat = get_satisfaction_score_average(db, s_dt, e_dt)

    return {
        "total_tickets": vol,
        "sla_breach_rate": sla_breach,
        "avg_csat": csat,
        "tickets_by_category": cats,
        "tickets_by_region": regs,
    }


@router.get("/inventory")
def get_inventory_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve stock levels, stockout rates, and low-inventory items."""
    s_dt = parse_date(start_date)
    e_dt = parse_date(end_date)

    st_rate = get_stockout_rate(db, s_dt, e_dt)
    cat_st = get_stockout_rate_by_category(db, s_dt, e_dt)
    units = get_units_sold(db, s_dt, e_dt)
    low_stock = get_low_inventory_products(db, threshold=10, limit=15)

    return {
        "overall_stockout_rate": st_rate,
        "stockout_rate_by_category": cat_st,
        "units_sold": units,
        "low_inventory_products": low_stock,
    }


@router.get("/marketing")
def get_marketing_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve marketing spend, conversions, ROAS, and channel performance."""
    s_dt = parse_date(start_date)
    e_dt = parse_date(end_date)

    summary = get_marketing_summary(db, s_dt, e_dt)
    channels = get_performance_by_channel(db, s_dt, e_dt)

    return {
        "summary": summary,
        "channel_breakdown": channels,
    }
