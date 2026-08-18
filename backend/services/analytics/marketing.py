"""
ORION Deterministic Analytics — Marketing Module

Calculates marketing spend, conversion metrics, attributed revenue, and ROAS.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.models import MarketingCampaign


def get_marketing_summary(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    channel: str | None = None,
    region: str | None = None,
) -> dict[str, Any]:
    """Aggregate all core marketing KPIs over the specified window."""
    query = select(
        func.coalesce(func.sum(MarketingCampaign.spend), 0.0),
        func.coalesce(func.sum(MarketingCampaign.impressions), 0),
        func.coalesce(func.sum(MarketingCampaign.clicks), 0),
        func.coalesce(func.sum(MarketingCampaign.conversions), 0),
        func.coalesce(func.sum(MarketingCampaign.attributed_revenue), 0.0),
        func.count(MarketingCampaign.id),
    )

    if start_date:
        query = query.where(MarketingCampaign.start_date >= start_date)
    if end_date:
        query = query.where(MarketingCampaign.end_date <= end_date)
    if channel:
        query = query.where(MarketingCampaign.channel == channel)
    if region:
        query = query.where(MarketingCampaign.region == region)

    spend, impr, clicks, conv, rev, camp_cnt = db.execute(query).one()

    spend = float(spend)
    impr = int(impr)
    clicks = int(clicks)
    conv = int(conv)
    rev = float(rev)

    ctr = (clicks / impr) if impr > 0 else 0.0
    cvr = (conv / clicks) if clicks > 0 else 0.0
    roas = (rev / spend) if spend > 0 else 0.0
    cac = (spend / conv) if conv > 0 else 0.0

    return {
        "total_spend": round(spend, 2),
        "total_impressions": impr,
        "total_clicks": clicks,
        "total_conversions": conv,
        "attributed_revenue": round(rev, 2),
        "click_through_rate": round(ctr, 4),
        "conversion_rate": round(cvr, 4),
        "roas": round(roas, 2),
        "customer_acquisition_cost": round(cac, 2),
        "campaigns_count": int(camp_cnt),
    }


def get_performance_by_channel(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict[str, Any]]:
    """Performance breakdown grouped by marketing channel."""
    query = (
        select(
            MarketingCampaign.channel,
            func.coalesce(func.sum(MarketingCampaign.spend), 0.0).label("spend"),
            func.coalesce(func.sum(MarketingCampaign.clicks), 0).label("clicks"),
            func.coalesce(func.sum(MarketingCampaign.conversions), 0).label("conversions"),
            func.coalesce(func.sum(MarketingCampaign.attributed_revenue), 0.0).label("revenue"),
        )
        .group_by(MarketingCampaign.channel)
    )
    if start_date:
        query = query.where(MarketingCampaign.start_date >= start_date)
    if end_date:
        query = query.where(MarketingCampaign.end_date <= end_date)

    rows = db.execute(query).all()
    results = []
    for ch, spend, clicks, convs, rev in rows:
        sp = float(spend)
        cl = int(clicks)
        co = int(convs)
        rv = float(rev)
        roas = (rv / sp) if sp > 0 else 0.0
        cvr = (co / cl) if cl > 0 else 0.0

        results.append({
            "channel": ch,
            "spend": round(sp, 2),
            "clicks": cl,
            "conversions": co,
            "attributed_revenue": round(rv, 2),
            "conversion_rate": round(cvr, 4),
            "roas": round(roas, 2),
        })

    return results
