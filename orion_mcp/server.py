"""
ORION Model Context Protocol (MCP) Server

Exposes ORION's deterministic analytics, multi-agent investigation pipeline,
human-in-the-loop governance, and safe action simulations to external agent runtimes.
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from orion_mcp.tools import (
    approve_recommendation as _approve_recommendation,
    calculate_business_impact as _calculate_business_impact,
    execute_approved_action as _execute_approved_action,
    get_anomaly_evidence as _get_anomaly_evidence,
    get_audit_events as _get_audit_events,
    get_business_anomalies as _get_business_anomalies,
    get_customer_analytics as _get_customer_analytics,
    get_inventory_analytics as _get_inventory_analytics,
    get_investigation as _get_investigation,
    get_marketing_analytics as _get_marketing_analytics,
    get_recommendations as _get_recommendations,
    get_revenue_analytics as _get_revenue_analytics,
    get_revenue_by_product as _get_revenue_by_product,
    get_revenue_by_region as _get_revenue_by_region,
    get_support_analytics as _get_support_analytics,
    reject_recommendation as _reject_recommendation,
    request_approval as _request_approval,
    start_investigation as _start_investigation,
)

# Initialize FastMCP Server
mcp = FastMCP(
    "orion-mcp",
    instructions="""
ORION is an enterprise AI Operations Intelligence and Autonomous Investigation System.
Use these tools to:
1. Detect operational anomalies across revenue, support, inventory, and marketing.
2. Retrieve deterministic evidence packages.
3. Trigger multi-agent causal investigations with statistical proof.
4. Calculate grounded realized and projected financial impacts.
5. Request and manage human executive approvals.
6. Execute safe operational simulations (support escalation, inventory restock, retention credits).
7. Inspect the tamper-evident operations audit trail.

CRITICAL GOVERNANCE:
No consequential action may execute without explicit human approval.
The backend remains the authoritative source of truth.
""",
)


# ==============================================================================
# MCP RESOURCES
# ==============================================================================

@mcp.resource("orion://capabilities")
def get_capabilities() -> str:
    """Explains ORION's business domains, deterministic analytics, and investigation pipeline."""
    return """
# ORION System Capabilities

1. Deterministic Analytics: SQL-grounded computations across 5 operational dimensions:
   - Revenue & Orders (52,000+ orders, daily timeseries, regional distributions)
   - Customer Retention (Cohorts, churn projections, repeat purchase rates)
   - Support Operations (Ticket volumes, SLA compliance, resolution times, CSAT)
   - Warehouse Inventory (Periodic snapshots, stockout rates, low stock alerts)
   - Marketing Campaigns (Ad spend, impressions, CTR, conversion rates, ROAS)

2. Multi-Agent Autonomous Investigation Pipeline:
   - DataAnalysisAgent: Statistical fact separation (OBSERVED, INFERRED, HYPOTHESIS)
   - AnomalyInvestigationAgent: Temporal onset & cross-dimensional correlation
   - RootCauseAgent: Hypothesis ranking based on evidence strength
   - BusinessImpactAgent: Deterministic financial loss calculations
   - RecommendationAgent: Ranked actionable mitigations
   - ActionAgent: Safe simulation execution

3. Human-in-the-Loop Governance:
   - State machine: PROPOSED -> PENDING_APPROVAL -> APPROVED / REJECTED -> EXECUTED
   - Action execution strictly blocked without authorization token.
"""


@mcp.resource("orion://safety-model")
def get_safety_model() -> str:
    """Explains the tool safety classification and authorization boundary."""
    return """
# ORION Tool Safety Classification Model

- READ_ONLY: Query deterministic data without modifying state or causing side effects.
  (get_business_anomalies, get_anomaly_evidence, get_*_analytics, get_investigation, get_audit_events)

- ANALYSIS: Computational synthesis and multi-agent reasoning.
  (start_investigation, calculate_business_impact)

- PROPOSAL: Generating or requesting mitigation proposals.
  (get_recommendations, request_approval)

- APPROVAL: Human operator authorization decision.
  (approve_recommendation, reject_recommendation)

- CONSEQUENTIAL_ACTION: Controlled domain operational execution.
  (execute_approved_action) — Strict human approval token required. Safe simulation mode.
"""


# ==============================================================================
# 1. READ-ONLY BUSINESS TOOLS
# ==============================================================================

@mcp.tool()
def get_business_anomalies(severity: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve currently detected statistical business anomalies across NovaCart operations.
    Safety: READ_ONLY
    """
    return _get_business_anomalies(severity)


@mcp.tool()
def get_anomaly_evidence(anomaly_id: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive quantitative evidence package for a specific business anomaly.
    Safety: READ_ONLY
    """
    return _get_anomaly_evidence(anomaly_id)


@mcp.tool()
def get_revenue_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = "daily",
) -> Dict[str, Any]:
    """
    Retrieve deterministic revenue analytics aggregated across the specified date window.
    Safety: READ_ONLY
    """
    return _get_revenue_analytics(start_date, end_date, granularity)


@mcp.tool()
def get_revenue_by_region(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve regional revenue distribution and order volumes across North, South, East, West.
    Safety: READ_ONLY
    """
    return _get_revenue_by_region(start_date, end_date)


@mcp.tool()
def get_revenue_by_product(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve product category revenue breakdown and top declining product SKUs.
    Safety: READ_ONLY
    """
    return _get_revenue_by_product(start_date, end_date)


@mcp.tool()
def get_customer_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve customer cohorts, repeat purchase rate, and customer segment distribution.
    Safety: READ_ONLY
    """
    return _get_customer_analytics(start_date, end_date)


@mcp.tool()
def get_support_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve customer support ticket volume, SLA breach rate, resolution hours, and CSAT scores.
    Safety: READ_ONLY
    """
    return _get_support_analytics(start_date, end_date)


@mcp.tool()
def get_inventory_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve warehouse stockout rates, category shortage alerts, and critically low inventory signals.
    Safety: READ_ONLY
    """
    return _get_inventory_analytics(start_date, end_date)


@mcp.tool()
def get_marketing_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve marketing ad spend, impressions, CTR, conversion rates, and Return on Ad Spend (ROAS).
    Safety: READ_ONLY
    """
    return _get_marketing_analytics(start_date, end_date)


# ==============================================================================
# 2. INVESTIGATION TOOLS
# ==============================================================================

@mcp.tool()
def start_investigation(anomaly_id: str) -> Dict[str, Any]:
    """
    Invoke the full multi-agent ORION investigation pipeline for a detected anomaly.
    Safety: ANALYSIS
    """
    return _start_investigation(anomaly_id)


@mcp.tool()
def get_investigation(investigation_id: str) -> Dict[str, Any]:
    """
    Retrieve full dossier and synthesis results for an existing investigation.
    Safety: READ_ONLY
    """
    return _get_investigation(investigation_id)


@mcp.tool()
def calculate_business_impact(anomaly_id: str = "ANOM-REV-001") -> Dict[str, Any]:
    """
    Compute deterministic business impact and financial loss projection using verified database figures.
    Safety: ANALYSIS
    """
    return _calculate_business_impact(anomaly_id)


# ==============================================================================
# 3. GOVERNANCE & RECOMMENDATION TOOLS
# ==============================================================================

@mcp.tool()
def get_recommendations(investigation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve prioritized, evidence-backed action recommendations.
    Safety: PROPOSAL
    """
    return _get_recommendations(investigation_id)


@mcp.tool()
def request_approval(recommendation_id: str) -> Dict[str, Any]:
    """
    Create a pending approval request for a proposed recommendation. Does NOT grant approval.
    Safety: PROPOSAL
    """
    return _request_approval(recommendation_id)


@mcp.tool()
def approve_recommendation(
    recommendation_id: str,
    approver: str = "ExecutiveOpsDirector",
    reason: str = "Approved via ORION MCP Governance Tool",
) -> Dict[str, Any]:
    """
    Formally grant executive human approval for a remediation proposal.
    Safety: APPROVAL
    """
    return _approve_recommendation(recommendation_id, approver, reason)


@mcp.tool()
def reject_recommendation(
    recommendation_id: str,
    approver: str = "ExecutiveOpsDirector",
    reason: str = "Rejected via ORION MCP Governance Tool",
) -> Dict[str, Any]:
    """
    Reject a proposed operational recommendation, permanently preventing execution.
    Safety: APPROVAL
    """
    return _reject_recommendation(recommendation_id, approver, reason)


# ==============================================================================
# 4. ACTION TOOL
# ==============================================================================

@mcp.tool()
def execute_approved_action(
    action_id: str,
    approval_id: str,
    investigation_id: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute an approved operational remediation action in safe simulation mode.
    Requires valid approval token.
    Safety: CONSEQUENTIAL_ACTION
    """
    return _execute_approved_action(action_id, approval_id, investigation_id, parameters)


# ==============================================================================
# 5. AUDIT TOOL
# ==============================================================================

@mcp.tool()
def get_audit_events(
    entity_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Retrieve chronological audit trail entries from ORION's immutable operational event log.
    Safety: READ_ONLY
    """
    return _get_audit_events(entity_id, event_type, limit)


if __name__ == "__main__":
    mcp.run()
