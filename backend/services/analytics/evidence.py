"""
ORION Evidence Package Generator

Assembles comprehensive, deterministic factual evidence across all operational dimensions
for a detected anomaly. Provides raw quantitative backing for future agent reasoning.
Zero hallucinated data — 100% computed from verified SQL queries.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.services.analytics.anomalies import AnomalyResult
from backend.services.analytics.customers import (
    get_customer_revenue_stats,
    get_customer_segment_distribution,
    get_new_customers,
    get_repeat_customers,
    get_repeat_purchase_rate,
)
from backend.services.analytics.inventory import (
    get_low_inventory_products,
    get_stockout_rate,
    get_stockout_rate_by_category,
    get_units_sold,
)
from backend.services.analytics.marketing import (
    get_marketing_summary,
    get_performance_by_channel,
)
from backend.services.analytics.orders import (
    get_average_order_value,
    get_cancellation_rate,
    get_order_status_distribution,
    get_order_volume,
)
from backend.services.analytics.revenue import (
    get_revenue_by_category,
    get_revenue_by_customer_segment,
    get_revenue_by_product,
    get_revenue_by_region,
    get_total_revenue,
)
from backend.services.analytics.support import (
    get_average_resolution_time,
    get_median_resolution_time,
    get_satisfaction_score_average,
    get_sla_breach_rate,
    get_tickets_by_category,
    get_tickets_by_region,
    get_ticket_volume,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RevenueEvidence(BaseModel):
    baseline_revenue: float
    evaluation_revenue: float
    change_percentage: float
    by_region_baseline: dict[str, float]
    by_region_evaluation: dict[str, float]
    by_category_baseline: dict[str, float]
    by_category_evaluation: dict[str, float]
    by_segment_baseline: dict[str, float]
    by_segment_evaluation: dict[str, float]
    top_declining_products: list[dict[str, Any]]


class SupportEvidence(BaseModel):
    baseline_ticket_volume: int
    evaluation_ticket_volume: int
    baseline_avg_resolution_hours: float
    evaluation_avg_resolution_hours: float
    baseline_median_resolution_hours: float
    evaluation_median_resolution_hours: float
    baseline_sla_breach_rate: float
    evaluation_sla_breach_rate: float
    baseline_csat: float
    evaluation_csat: float
    tickets_by_category: dict[str, int]
    tickets_by_region: dict[str, int]


class InventoryEvidence(BaseModel):
    baseline_stockout_rate: float
    evaluation_stockout_rate: float
    stockout_rate_by_category: dict[str, float]
    units_sold_baseline: int
    units_sold_evaluation: int
    critically_low_products: list[dict[str, Any]]


class CustomerEvidence(BaseModel):
    baseline_repeat_purchase_rate: float
    evaluation_repeat_purchase_rate: float
    new_customers_acquired: int
    repeat_customers_evaluation: int
    segment_distribution: dict[str, int]


class MarketingEvidence(BaseModel):
    total_spend: float
    total_conversions: int
    conversion_rate: float
    attributed_revenue: float
    roas: float
    channel_performance: list[dict[str, Any]]


class EvidencePackage(BaseModel):
    """Complete quantitative dossier supporting an anomaly investigation."""
    anomaly_id: str
    target_metric: str
    baseline_window: dict[str, str]
    evaluation_window: dict[str, str]
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    revenue: RevenueEvidence
    support: SupportEvidence
    inventory: InventoryEvidence
    customers: CustomerEvidence
    marketing: MarketingEvidence


# ---------------------------------------------------------------------------
# Generator Service
# ---------------------------------------------------------------------------

def generate_evidence_package(
    db: Session,
    anomaly: AnomalyResult,
    baseline_start: datetime,
    baseline_end: datetime,
    evaluation_start: datetime,
    evaluation_end: datetime,
) -> EvidencePackage:
    """
    Construct a verified, multi-dimensional EvidencePackage across all operations.
    """
    # 1. Revenue Evidence
    rev_base = get_total_revenue(db, baseline_start, baseline_end)
    rev_eval = get_total_revenue(db, evaluation_start, evaluation_end)
    rev_change_pct = ((rev_eval - rev_base) / rev_base * 100.0) if rev_base > 0 else 0.0

    reg_base = get_revenue_by_region(db, baseline_start, baseline_end)
    reg_eval = get_revenue_by_region(db, evaluation_start, evaluation_end)
    cat_base = get_revenue_by_category(db, baseline_start, baseline_end)
    cat_eval = get_revenue_by_category(db, evaluation_start, evaluation_end)
    seg_base = get_revenue_by_customer_segment(db, baseline_start, baseline_end)
    seg_eval = get_revenue_by_customer_segment(db, evaluation_start, evaluation_end)
    top_prods_eval = get_revenue_by_product(db, evaluation_start, evaluation_end, limit=10)

    revenue_ev = RevenueEvidence(
        baseline_revenue=round(rev_base, 2),
        evaluation_revenue=round(rev_eval, 2),
        change_percentage=round(rev_change_pct, 2),
        by_region_baseline=reg_base,
        by_region_evaluation=reg_eval,
        by_category_baseline=cat_base,
        by_category_evaluation=cat_eval,
        by_segment_baseline=seg_base,
        by_segment_evaluation=seg_eval,
        top_declining_products=top_prods_eval,
    )

    # 2. Support Evidence
    sup_vol_base = get_ticket_volume(db, baseline_start, baseline_end)
    sup_vol_eval = get_ticket_volume(db, evaluation_start, evaluation_end)
    sup_avg_res_base = get_average_resolution_time(db, baseline_start, baseline_end)
    sup_avg_res_eval = get_average_resolution_time(db, evaluation_start, evaluation_end)
    sup_med_res_base = get_median_resolution_time(db, baseline_start, baseline_end)
    sup_med_res_eval = get_median_resolution_time(db, evaluation_start, evaluation_end)
    sup_sla_base = get_sla_breach_rate(db, baseline_start, baseline_end)
    sup_sla_eval = get_sla_breach_rate(db, evaluation_start, evaluation_end)
    sup_csat_base = get_satisfaction_score_average(db, baseline_start, baseline_end)
    sup_csat_eval = get_satisfaction_score_average(db, evaluation_start, evaluation_end)
    tcks_by_cat = get_tickets_by_category(db, evaluation_start, evaluation_end)
    tcks_by_reg = get_tickets_by_region(db, evaluation_start, evaluation_end)

    support_ev = SupportEvidence(
        baseline_ticket_volume=sup_vol_base,
        evaluation_ticket_volume=sup_vol_eval,
        baseline_avg_resolution_hours=sup_avg_res_base,
        evaluation_avg_resolution_hours=sup_avg_res_eval,
        baseline_median_resolution_hours=sup_med_res_base,
        evaluation_median_resolution_hours=sup_med_res_eval,
        baseline_sla_breach_rate=sup_sla_base,
        evaluation_sla_breach_rate=sup_sla_eval,
        baseline_csat=sup_csat_base,
        evaluation_csat=sup_csat_eval,
        tickets_by_category=tcks_by_cat,
        tickets_by_region=tcks_by_reg,
    )

    # 3. Inventory Evidence
    inv_st_base = get_stockout_rate(db, baseline_start, baseline_end)
    inv_st_eval = get_stockout_rate(db, evaluation_start, evaluation_end)
    inv_st_cat = get_stockout_rate_by_category(db, evaluation_start, evaluation_end)
    units_sold_base = get_units_sold(db, baseline_start, baseline_end)
    units_sold_eval = get_units_sold(db, evaluation_start, evaluation_end)
    crit_prods = get_low_inventory_products(db, threshold=10, limit=10)

    inventory_ev = InventoryEvidence(
        baseline_stockout_rate=inv_st_base,
        evaluation_stockout_rate=inv_st_eval,
        stockout_rate_by_category=inv_st_cat,
        units_sold_baseline=units_sold_base,
        units_sold_evaluation=units_sold_eval,
        critically_low_products=crit_prods,
    )

    # 4. Customer Evidence
    cust_rep_base = get_repeat_purchase_rate(db, baseline_start, baseline_end)
    cust_rep_eval = get_repeat_purchase_rate(db, evaluation_start, evaluation_end)
    new_custs = get_new_customers(db, evaluation_start, evaluation_end)
    rep_custs = get_repeat_customers(db, evaluation_start, evaluation_end)
    seg_dist = get_customer_segment_distribution(db)

    customer_ev = CustomerEvidence(
        baseline_repeat_purchase_rate=cust_rep_base,
        evaluation_repeat_purchase_rate=cust_rep_eval,
        new_customers_acquired=new_custs,
        repeat_customers_evaluation=rep_custs,
        segment_distribution=seg_dist,
    )

    # 5. Marketing Evidence
    mktg_sum = get_marketing_summary(db, evaluation_start, evaluation_end)
    mktg_chan = get_performance_by_channel(db, evaluation_start, evaluation_end)

    marketing_ev = MarketingEvidence(
        total_spend=mktg_sum["total_spend"],
        total_conversions=mktg_sum["total_conversions"],
        conversion_rate=mktg_sum["conversion_rate"],
        attributed_revenue=mktg_sum["attributed_revenue"],
        roas=mktg_sum["roas"],
        channel_performance=mktg_chan,
    )

    return EvidencePackage(
        anomaly_id=anomaly.anomaly_id,
        target_metric=anomaly.metric,
        baseline_window={"start": str(baseline_start.date()), "end": str(baseline_end.date())},
        evaluation_window={"start": str(evaluation_start.date()), "end": str(evaluation_end.date())},
        revenue=revenue_ev,
        support=support_ev,
        inventory=inventory_ev,
        customers=customer_ev,
        marketing=marketing_ev,
    )
