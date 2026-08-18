"""
ORION Deterministic Analytics — Revenue Module

Performs SQL/Python calculations for revenue metrics across time,
regions, products, categories, and customer segments.
No LLM estimation — pure database aggregation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.models import Customer, Order, OrderStatus, Product


def get_total_revenue(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    region: str | None = None,
    status: str = OrderStatus.COMPLETED.value,
) -> float:
    """Calculate gross revenue for completed orders within a time window."""
    query = select(func.coalesce(func.sum(Order.total_amount), 0.0)).where(Order.status == status)

    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)
    if region:
        query = query.where(Order.region == region)

    val = db.execute(query).scalar_one()
    return float(val)


def get_daily_revenue(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    region: str | None = None,
) -> list[dict[str, Any]]:
    """Aggregate revenue by date string YYYY-MM-DD."""
    # Using func.substr or strftime compatible with SQLite and PostgreSQL
    # For universal portability, fetch and bucket or use func.date
    query = (
        select(
            Order.order_date,
            Order.total_amount,
        )
        .where(Order.status == OrderStatus.COMPLETED.value)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)
    if region:
        query = query.where(Order.region == region)

    rows = db.execute(query).all()
    daily_map: dict[str, float] = {}
    for dt, amt in rows:
        d_str = dt.strftime("%Y-%m-%d")
        daily_map[d_str] = daily_map.get(d_str, 0.0) + float(amt)

    result = [{"date": d, "revenue": round(rev, 2)} for d, rev in sorted(daily_map.items())]
    return result


def get_weekly_revenue(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict[str, Any]]:
    """Aggregate revenue by ISO calendar week (YYYY-Wxx)."""
    query = (
        select(Order.order_date, Order.total_amount)
        .where(Order.status == OrderStatus.COMPLETED.value)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    rows = db.execute(query).all()
    weekly_map: dict[str, float] = {}
    for dt, amt in rows:
        w_str = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
        weekly_map[w_str] = weekly_map.get(w_str, 0.0) + float(amt)

    return [{"week": w, "revenue": round(rev, 2)} for w, rev in sorted(weekly_map.items())]


def get_monthly_revenue(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict[str, Any]]:
    """Aggregate revenue by month (YYYY-MM)."""
    query = (
        select(Order.order_date, Order.total_amount)
        .where(Order.status == OrderStatus.COMPLETED.value)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    rows = db.execute(query).all()
    monthly_map: dict[str, float] = {}
    for dt, amt in rows:
        m_str = dt.strftime("%Y-%m")
        monthly_map[m_str] = monthly_map.get(m_str, 0.0) + float(amt)

    return [{"month": m, "revenue": round(rev, 2)} for m, rev in sorted(monthly_map.items())]


def get_revenue_by_region(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, float]:
    """Breakdown total revenue by sales region."""
    query = (
        select(
            Order.region,
            func.coalesce(func.sum(Order.total_amount), 0.0),
        )
        .where(Order.status == OrderStatus.COMPLETED.value)
        .group_by(Order.region)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    rows = db.execute(query).all()
    return {region: round(float(total), 2) for region, total in rows}


def get_revenue_by_product(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Top products ranked by total revenue."""
    query = (
        select(
            Product.product_id,
            Product.name,
            Product.category,
            func.coalesce(func.sum(Order.total_amount), 0.0).label("total_rev"),
            func.count(Order.id).label("order_count"),
        )
        .join(Order, Product.id == Order.product_id)
        .where(Order.status == OrderStatus.COMPLETED.value)
        .group_by(Product.product_id, Product.name, Product.category)
        .order_by(func.sum(Order.total_amount).desc())
        .limit(limit)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    rows = db.execute(query).all()
    return [
        {
            "product_id": pid,
            "name": name,
            "category": cat,
            "revenue": round(float(rev), 2),
            "order_count": int(cnt),
        }
        for pid, name, cat, rev, cnt in rows
    ]


def get_revenue_by_category(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, float]:
    """Breakdown total revenue by product category."""
    query = (
        select(
            Product.category,
            func.coalesce(func.sum(Order.total_amount), 0.0),
        )
        .join(Order, Product.id == Order.product_id)
        .where(Order.status == OrderStatus.COMPLETED.value)
        .group_by(Product.category)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    rows = db.execute(query).all()
    return {cat: round(float(total), 2) for cat, total in rows}


def get_revenue_by_customer_segment(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, float]:
    """Breakdown total revenue by customer segment (VIP, Regular, At-Risk, etc.)."""
    query = (
        select(
            Customer.segment,
            func.coalesce(func.sum(Order.total_amount), 0.0),
        )
        .join(Order, Customer.id == Order.customer_id)
        .where(Order.status == OrderStatus.COMPLETED.value)
        .group_by(Customer.segment)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    rows = db.execute(query).all()
    return {segment: round(float(total), 2) for segment, total in rows}
