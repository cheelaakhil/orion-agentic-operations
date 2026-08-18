"""
ORION MCP Tools Package

Exports all 18 business operations, investigation, governance, and audit tools.
"""

from orion_mcp.tools.read_only import (
    get_business_anomalies,
    get_anomaly_evidence,
    get_revenue_analytics,
    get_revenue_by_region,
    get_revenue_by_product,
    get_customer_analytics,
    get_support_analytics,
    get_inventory_analytics,
    get_marketing_analytics,
)
from orion_mcp.tools.investigation import (
    start_investigation,
    get_investigation,
    calculate_business_impact,
)
from orion_mcp.tools.governance import (
    get_recommendations,
    request_approval,
    approve_recommendation,
    reject_recommendation,
)
from orion_mcp.tools.action import (
    execute_approved_action,
)
from orion_mcp.tools.audit import (
    get_audit_events,
)

TOOL_SAFETY_CLASSIFICATIONS = {
    "get_business_anomalies": "READ_ONLY",
    "get_anomaly_evidence": "READ_ONLY",
    "get_revenue_analytics": "READ_ONLY",
    "get_revenue_by_region": "READ_ONLY",
    "get_revenue_by_product": "READ_ONLY",
    "get_customer_analytics": "READ_ONLY",
    "get_support_analytics": "READ_ONLY",
    "get_inventory_analytics": "READ_ONLY",
    "get_marketing_analytics": "READ_ONLY",
    "start_investigation": "ANALYSIS",
    "get_investigation": "READ_ONLY",
    "calculate_business_impact": "ANALYSIS",
    "get_recommendations": "PROPOSAL",
    "request_approval": "PROPOSAL",
    "approve_recommendation": "APPROVAL",
    "reject_recommendation": "APPROVAL",
    "execute_approved_action": "CONSEQUENTIAL_ACTION",
    "get_audit_events": "READ_ONLY",
}

__all__ = [
    "get_business_anomalies",
    "get_anomaly_evidence",
    "get_revenue_analytics",
    "get_revenue_by_region",
    "get_revenue_by_product",
    "get_customer_analytics",
    "get_support_analytics",
    "get_inventory_analytics",
    "get_marketing_analytics",
    "start_investigation",
    "get_investigation",
    "calculate_business_impact",
    "get_recommendations",
    "request_approval",
    "approve_recommendation",
    "reject_recommendation",
    "execute_approved_action",
    "get_audit_events",
    "TOOL_SAFETY_CLASSIFICATIONS",
]
