"""
ORION Deterministic Analytics — Customer Metrics Module

Calculates customer cohorts, retention, repeat purchase rates, and segment distribution.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.models import Customer, Order, OrderStatus


def get_total_customers(
    db: Session,
    as_of_date: datetime | None = None,
) -> int:
    """Total registered customer count."""
    query = select(func.count(Customer.id))
    if as_of_date:
        query = query.where(Customer.created_at <= as_of_date)
    return int(db.execute(query).scalar_one())


def get_new_customers(
    db: Session,
    start_date: datetime,
    end_date: datetime,
) -> int:
    """New customers acquired within the specified period."""
    query = (
        select(func.count(Customer.id))
        .where(Customer.created_at >= start_date)
        .where(Customer.created_at <= end_date)
    )
    return int(db.execute(query).scalar_one())


def get_repeat_customers(
    db: Session,
    start_date: datetime,
    end_date: datetime,
) -> int:
    """Count of customers who placed 2 or more completed orders in the period."""
    subq = (
        select(Order.customer_id)
        .where(Order.status == OrderStatus.COMPLETED.value)
        .where(Order.order_date >= start_date)
        .where(Order.order_date <= end_date)
        .group_by(Order.customer_id)
        .having(func.count(Order.id) >= 2)
    ).subquery()

    query = select(func.count()).select_from(subq)
    return int(db.execute(query).scalar_one())


def get_repeat_purchase_rate(
    db: Session,
    start_date: datetime,
    end_date: datetime,
) -> float:
    """
    Calculate repeat purchase rate:
    (Customers with >=2 orders in period) / (Customers with >=1 order in period)
    """
    # Total unique active buyers in period
    active_buyers_query = (
        select(func.count(func.distinct(Order.customer_id)))
        .where(Order.status == OrderStatus.COMPLETED.value)
        .where(Order.order_date >= start_date)
        .where(Order.order_date <= end_date)
    )
    total_active_buyers = db.execute(active_buyers_query).scalar_one() or 0

    if total_active_buyers == 0:
        return 0.0

    repeat_buyers = get_repeat_customers(db, start_date, end_date)
    return round(float(repeat_buyers) / float(total_active_buyers), 4)


def get_customer_revenue_stats(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, float]:
    """Average revenue per customer and customer lifetime statistics."""
    query = (
        select(
            func.coalesce(func.sum(Order.total_amount), 0.0).label("total_rev"),
            func.count(func.distinct(Order.customer_id)).label("unique_customers"),
        )
        .where(Order.status == OrderStatus.COMPLETED.value)
    )
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    tot_rev, uniq_cust = db.execute(query).one()
    tot_rev = float(tot_rev)
    uniq_cust = int(uniq_cust)

    arpu = (tot_rev / uniq_cust) if uniq_cust > 0 else 0.0
    return {
        "total_revenue": round(tot_rev, 2),
        "unique_purchasing_customers": uniq_cust,
        "average_revenue_per_customer": round(arpu, 2),
    }


def get_customer_segment_distribution(
    db: Session,
) -> dict[str, int]:
    """Distribution of all customers across segments."""
    query = select(Customer.segment, func.count(Customer.id)).group_by(Customer.segment)
    rows = db.execute(query).all()
    return {seg: int(cnt) for seg, cnt in rows}
