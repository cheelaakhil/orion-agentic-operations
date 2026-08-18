"""
Unit tests for deterministic analytics modules across all operational dimensions.
"""

from datetime import datetime
import pytest

from backend.services.analytics import (
    get_average_order_value,
    get_average_resolution_time,
    get_cancellation_rate,
    get_customer_revenue_stats,
    get_customer_segment_distribution,
    get_daily_revenue,
    get_inventory_availability,
    get_low_inventory_products,
    get_marketing_summary,
    get_median_resolution_time,
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


# ---------------------------------------------------------------------------
# Revenue Tests
# ---------------------------------------------------------------------------

def test_revenue_calculations(populated_db):
    # May 1 to May 31: ORD-001 ($120), ORD-002 ($100), ORD-003 ($50), ORD-004 ($50), ORD-005 ($25) = $345.00
    may_rev = get_total_revenue(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_rev == 345.00

    # June 1 to June 30: ORD-006 ($25), ORD-007 ($50) = $75.00 (ORD-008 is CANCELLED)
    june_rev = get_total_revenue(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_rev == 75.00

    # Regional revenue
    reg_rev = get_revenue_by_region(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert reg_rev["North America"] == 220.00
    assert reg_rev["Europe"] == 100.00
    assert reg_rev["Asia-Pacific"] == 25.00

    # Category revenue
    cat_rev = get_revenue_by_category(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert cat_rev["Electronics"] == 120.00
    assert cat_rev["Home & Kitchen"] == 150.00
    assert cat_rev["Apparel"] == 75.00

    # Segment revenue
    seg_rev = get_revenue_by_customer_segment(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert seg_rev["VIP"] == 220.00
    assert seg_rev["REGULAR"] == 100.00
    assert seg_rev["AT_RISK"] == 25.00

    # Time series
    daily = get_daily_revenue(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert len(daily) == 5
    weekly = get_weekly_revenue(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert len(weekly) >= 1
    monthly = get_monthly_revenue(populated_db, datetime(2026, 5, 1), datetime(2026, 6, 30))
    assert len(monthly) == 2


# ---------------------------------------------------------------------------
# Customer Tests
# ---------------------------------------------------------------------------

def test_customer_metrics(populated_db):
    tot = get_total_customers(populated_db)
    assert tot == 3

    # In May, c1 (2 orders), c2 (2 orders), c3 (1 order) -> 2 repeat customers out of 3 active buyers
    may_repeat = get_repeat_customers(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_repeat == 2
    may_rate = get_repeat_purchase_rate(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_rate == round(2.0 / 3.0, 4)

    # In June, c1 (1 order), c2 (1 order), c3 (1 cancelled) -> 0 repeat customers in June
    june_repeat = get_repeat_customers(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_repeat == 0

    stats = get_customer_revenue_stats(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert stats["unique_purchasing_customers"] == 3
    assert stats["total_revenue"] == 345.00

    segs = get_customer_segment_distribution(populated_db)
    assert segs["VIP"] == 1
    assert segs["REGULAR"] == 1
    assert segs["AT_RISK"] == 1


# ---------------------------------------------------------------------------
# Order Tests
# ---------------------------------------------------------------------------

def test_order_metrics(populated_db):
    may_vol = get_order_volume(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_vol == 5

    may_aov = get_average_order_value(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_aov == round(345.00 / 5, 2)

    # June cancellation rate: 1 cancelled out of 3 total = 33.33%
    june_canc = get_cancellation_rate(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_canc == round(1.0 / 3.0, 4)

    dist = get_order_status_distribution(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert dist["COMPLETED"] == 2
    assert dist["CANCELLED"] == 1


# ---------------------------------------------------------------------------
# Inventory Tests
# ---------------------------------------------------------------------------

def test_inventory_metrics(populated_db):
    # May stockout rate: 0 stockouts out of 3 snapshots = 0%
    may_stockout = get_stockout_rate(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_stockout == 0.0

    # June stockout rate: 1 stockout (p1 in NA) out of 3 snapshots = 33.33%
    june_stockout = get_stockout_rate(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_stockout == round(1.0 / 3.0, 4)

    cat_stock = get_stockout_rate_by_category(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert cat_stock["Electronics"] == 1.0  # 1 of 1 snap out of stock
    assert cat_stock["Home & Kitchen"] == 0.0

    units = get_units_sold(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert units == 7  # 1+2+1+2+1

    low = get_low_inventory_products(populated_db, threshold=10)
    assert len(low) == 1
    assert low[0]["product_id"] == "PROD-001"


# ---------------------------------------------------------------------------
# Support Tests
# ---------------------------------------------------------------------------

def test_support_metrics(populated_db):
    may_vol = get_ticket_volume(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_vol == 2

    # May SLA breach rate: 0 breached out of 2 = 0%
    may_sla = get_sla_breach_rate(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_sla == 0.0

    # June SLA breach rate: 2 breached out of 2 = 100%
    june_sla = get_sla_breach_rate(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_sla == 1.0

    # Resolution hours
    may_avg_res = get_average_resolution_time(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_avg_res == 1.75  # (1.5 + 2.0) / 2

    june_avg_res = get_average_resolution_time(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_avg_res == 30.25  # (32.0 + 28.5) / 2

    june_med_res = get_median_resolution_time(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_med_res == 30.25

    # CSAT
    may_csat = get_satisfaction_score_average(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_csat == 4.5
    june_csat = get_satisfaction_score_average(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_csat == 1.0


# ---------------------------------------------------------------------------
# Marketing Tests
# ---------------------------------------------------------------------------

def test_marketing_metrics(populated_db):
    may_mktg = get_marketing_summary(populated_db, datetime(2026, 5, 1), datetime(2026, 5, 31))
    assert may_mktg["total_spend"] == 1000.00
    assert may_mktg["total_conversions"] == 100
    assert may_mktg["conversion_rate"] == 0.05
    assert may_mktg["roas"] == 5.0

    june_mktg = get_marketing_summary(populated_db, datetime(2026, 6, 1), datetime(2026, 6, 30))
    assert june_mktg["total_spend"] == 1000.00
    assert june_mktg["total_conversions"] == 35
    assert june_mktg["roas"] == 1.75

    channels = get_performance_by_channel(populated_db, datetime(2026, 5, 1), datetime(2026, 6, 30))
    assert len(channels) == 2
