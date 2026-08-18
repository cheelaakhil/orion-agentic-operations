"""
ORION Deterministic Analytics — Orders Module

Computes order volume, AOV, cancellation rates, and fulfillment status distribution.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.models import Order, OrderStatus


def get_order_volume(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    status: str | None = None,
) -> int:
    """Total order count matching parameters."""
    query = select(func.count(Order.id))
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)
    if status:
        query = query.where(Order.status == status)

    return int(db.execute(query).scalar_one())


def get_average_order_value(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    region: str | None = None,
) -> float:
    """Average order value (AOV) for completed orders."""
    query = select(func.avg(Order.total_amount)).where(Order.status == OrderStatus.COMPLETED.value)
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)
    if region:
        query = query.where(Order.region == region)

    val = db.execute(query).scalar_one()
    return round(float(val or 0.0), 2)


def get_cancellation_rate(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> float:
    """Ratio of CANCELLED orders to total orders placed."""
    total_query = select(func.count(Order.id))
    cancelled_query = select(func.count(Order.id)).where(Order.status == OrderStatus.CANCELLED.value)

    if start_date:
        total_query = total_query.where(Order.order_date >= start_date)
        cancelled_query = cancelled_query.where(Order.order_date >= start_date)
    if end_date:
        total_query = total_query.where(Order.order_date <= end_date)
        cancelled_query = cancelled_query.where(Order.order_date <= end_date)

    total = db.execute(total_query).scalar_one() or 0
    cancelled = db.execute(cancelled_query).scalar_one() or 0

    if total == 0:
        return 0.0
    return round(float(cancelled) / float(total), 4)


def get_order_status_distribution(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, int]:
    """Breakdown of orders by status (COMPLETED, CANCELLED, PENDING, REFUNDED)."""
    query = select(Order.status, func.count(Order.id)).group_by(Order.status)
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    rows = db.execute(query).all()
    return {st: int(cnt) for st, cnt in rows}
