"""
ORION Deterministic Analytics — Support Operations Module

Calculates ticket volume, resolution duration, median resolution, SLA breach rates,
and category/regional breakdown.
"""

from datetime import datetime
from typing import Any

import numpy as np
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.models import SupportTicket


def get_ticket_volume(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str | None = None,
    region: str | None = None,
) -> int:
    """Total support ticket count matching criteria."""
    query = select(func.count(SupportTicket.id))
    if start_date:
        query = query.where(SupportTicket.created_at >= start_date)
    if end_date:
        query = query.where(SupportTicket.created_at <= end_date)
    if category:
        query = query.where(SupportTicket.category == category)
    if region:
        query = query.where(SupportTicket.region == region)

    return int(db.execute(query).scalar_one())


def get_average_resolution_time(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    region: str | None = None,
) -> float:
    """Average resolution time in hours for resolved tickets."""
    query = select(func.avg(SupportTicket.resolution_time_hours)).where(
        SupportTicket.resolution_time_hours.isnot(None)
    )
    if start_date:
        query = query.where(SupportTicket.created_at >= start_date)
    if end_date:
        query = query.where(SupportTicket.created_at <= end_date)
    if region:
        query = query.where(SupportTicket.region == region)

    val = db.execute(query).scalar_one()
    return round(float(val or 0.0), 2)


def get_median_resolution_time(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    region: str | None = None,
) -> float:
    """Deterministic median resolution time in hours computed via numpy."""
    query = select(SupportTicket.resolution_time_hours).where(
        SupportTicket.resolution_time_hours.isnot(None)
    )
    if start_date:
        query = query.where(SupportTicket.created_at >= start_date)
    if end_date:
        query = query.where(SupportTicket.created_at <= end_date)
    if region:
        query = query.where(SupportTicket.region == region)

    rows = db.execute(query).scalars().all()
    if not rows:
        return 0.0

    median_val = float(np.median(rows))
    return round(median_val, 2)


def get_sla_breach_rate(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    region: str | None = None,
) -> float:
    """Ratio of SLA breached tickets to total tickets."""
    total_query = select(func.count(SupportTicket.id))
    breached_query = select(func.count(SupportTicket.id)).where(SupportTicket.sla_breached == True)

    if start_date:
        total_query = total_query.where(SupportTicket.created_at >= start_date)
        breached_query = breached_query.where(SupportTicket.created_at >= start_date)
    if end_date:
        total_query = total_query.where(SupportTicket.created_at <= end_date)
        breached_query = breached_query.where(SupportTicket.created_at <= end_date)
    if region:
        total_query = total_query.where(SupportTicket.region == region)
        breached_query = breached_query.where(SupportTicket.region == region)

    total = db.execute(total_query).scalar_one() or 0
    breached = db.execute(breached_query).scalar_one() or 0

    if total == 0:
        return 0.0
    return round(float(breached) / float(total), 4)


def get_tickets_by_category(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, int]:
    """Breakdown of support tickets by category."""
    query = select(SupportTicket.category, func.count(SupportTicket.id)).group_by(SupportTicket.category)
    if start_date:
        query = query.where(SupportTicket.created_at >= start_date)
    if end_date:
        query = query.where(SupportTicket.created_at <= end_date)

    rows = db.execute(query).all()
    return {cat: int(cnt) for cat, cnt in rows}


def get_tickets_by_region(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, int]:
    """Breakdown of support tickets by customer region."""
    query = select(SupportTicket.region, func.count(SupportTicket.id)).group_by(SupportTicket.region)
    if start_date:
        query = query.where(SupportTicket.created_at >= start_date)
    if end_date:
        query = query.where(SupportTicket.created_at <= end_date)

    rows = db.execute(query).all()
    return {reg: int(cnt) for reg, cnt in rows}


def get_satisfaction_score_average(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> float:
    """Average customer satisfaction rating (1-5 scale)."""
    query = select(func.avg(SupportTicket.satisfaction_score)).where(
        SupportTicket.satisfaction_score.isnot(None)
    )
    if start_date:
        query = query.where(SupportTicket.created_at >= start_date)
    if end_date:
        query = query.where(SupportTicket.created_at <= end_date)

    val = db.execute(query).scalar_one()
    return round(float(val or 0.0), 2)
