"""
ORION Ground Truth Configuration (Evaluation Only)

This module defines the engineered business incident parameters embedded into the
NovaCart synthetic dataset. It is strictly used for testing and evaluation harnesses
to measure if analytics services and future AI agents accurately identify the true
contributing factors and quantify the impact.

CRITICAL: This configuration is NOT exposed through production database tables or APIs.
The system must discover these insights purely through deterministic analytics and reasoning.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class GroundTruthIncident:
    """Ground truth details of the engineered NovaCart operational breakdown."""

    company_name: str = "NovaCart"
    simulation_start_date: str = "2026-05-01"
    simulation_end_date: str = "2026-08-01"
    incident_onset_date: str = "2026-06-20"  # Final ~6 weeks

    # Contributing Factors
    factor_1_support_sla_deterioration: dict[str, Any] = field(default_factory=lambda: {
        "description": "Severe support team understaffing after summer promotion launch",
        "affected_regions": ["North America", "Europe", "Asia-Pacific", "Latin America"],
        "baseline_avg_resolution_hours": 2.2,
        "incident_avg_resolution_hours": 26.5,
        "baseline_sla_breach_rate": 0.04,  # 4%
        "incident_sla_breach_rate": 0.38,  # 38%
        "impact_channel": "Customer dissatisfaction driving down repeat purchase rate",
    })

    factor_2_category_stockouts: dict[str, Any] = field(default_factory=lambda: {
        "description": "Supply chain warehouse bottleneck causing stockouts in top-selling categories",
        "affected_categories": ["Electronics", "Home & Kitchen"],
        "baseline_stockout_rate": 0.03,  # 3%
        "incident_stockout_rate": 0.28,  # 28%
        "impact_channel": "Lost high-ticket orders and unfulfilled cart conversions",
    })

    # Compounding Downstream Outcomes
    expected_revenue_decline_pct: float = -23.5  # ~23.5% decline period-over-period
    expected_repeat_purchase_rate_baseline: float = 0.34  # 34%
    expected_repeat_purchase_rate_incident: float = 0.19  # 19%
    expected_order_volume_decline_pct: float = -18.0
    expected_aov_decline_pct: float = -6.5

    # Evaluation Scoring Criteria
    key_signals_to_detect: list[str] = field(default_factory=lambda: [
        "REVENUE_DROP",
        "SUPPORT_SLA_BREACH_SPIKE",
        "SUPPORT_RESOLUTION_TIME_SPIKE",
        "INVENTORY_STOCKOUT_SPIKE",
        "REPEAT_PURCHASE_RATE_DROP",
        "CATEGORY_REVENUE_IMBALANCE_ELECTRONICS",
    ])


GROUND_TRUTH = GroundTruthIncident()
