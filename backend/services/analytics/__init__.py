"""
ORION Deterministic Analytics Services Package
"""

from .anomalies import (
    AnomalyResult,
    AnomalySeverity,
    AnomalyThresholds,
    DeterministicAnomalyEngine,
    anomaly_engine,
)
from .customers import (
    get_customer_revenue_stats,
    get_customer_segment_distribution,
    get_new_customers,
    get_repeat_customers,
    get_repeat_purchase_rate,
    get_total_customers,
)
from .evidence import (
    CustomerEvidence,
    EvidencePackage,
    InventoryEvidence,
    MarketingEvidence,
    RevenueEvidence,
    SupportEvidence,
    generate_evidence_package,
)
from .inventory import (
    get_inventory_availability,
    get_low_inventory_products,
    get_stockout_rate,
    get_stockout_rate_by_category,
    get_units_sold,
)
from .marketing import (
    get_marketing_summary,
    get_performance_by_channel,
)
from .orders import (
    get_average_order_value,
    get_cancellation_rate,
    get_order_status_distribution,
    get_order_volume,
)
from .revenue import (
    get_daily_revenue,
    get_monthly_revenue,
    get_revenue_by_category,
    get_revenue_by_customer_segment,
    get_revenue_by_product,
    get_revenue_by_region,
    get_total_revenue,
    get_weekly_revenue,
)
from .support import (
    get_average_resolution_time,
    get_median_resolution_time,
    get_satisfaction_score_average,
    get_sla_breach_rate,
    get_tickets_by_category,
    get_tickets_by_region,
    get_ticket_volume,
)

__all__ = [
    # Revenue
    "get_total_revenue",
    "get_daily_revenue",
    "get_weekly_revenue",
    "get_monthly_revenue",
    "get_revenue_by_region",
    "get_revenue_by_product",
    "get_revenue_by_category",
    "get_revenue_by_customer_segment",
    # Customers
    "get_total_customers",
    "get_new_customers",
    "get_repeat_customers",
    "get_repeat_purchase_rate",
    "get_customer_revenue_stats",
    "get_customer_segment_distribution",
    # Orders
    "get_order_volume",
    "get_average_order_value",
    "get_cancellation_rate",
    "get_order_status_distribution",
    # Inventory
    "get_inventory_availability",
    "get_stockout_rate",
    "get_stockout_rate_by_category",
    "get_units_sold",
    "get_low_inventory_products",
    # Support
    "get_ticket_volume",
    "get_average_resolution_time",
    "get_median_resolution_time",
    "get_sla_breach_rate",
    "get_tickets_by_category",
    "get_tickets_by_region",
    "get_satisfaction_score_average",
    # Marketing
    "get_marketing_summary",
    "get_performance_by_channel",
    # Anomalies
    "AnomalyResult",
    "AnomalySeverity",
    "AnomalyThresholds",
    "DeterministicAnomalyEngine",
    "anomaly_engine",
    # Evidence
    "EvidencePackage",
    "RevenueEvidence",
    "SupportEvidence",
    "InventoryEvidence",
    "CustomerEvidence",
    "MarketingEvidence",
    "generate_evidence_package",
]
