"""
ORION MCP Tool Layer Integration Test Suite

Tests:
1. Discovery and registration of all 18 MCP tools
2. Read-only analytics tools
3. Multi-agent investigation invocation
4. Business impact calculations
5. Recommendation retrieval
6. Human approval enforcement & rejection logic
7. Safe simulated action execution
8. Audit trail event recording
"""

import pytest
from sqlalchemy.orm import Session
from orion_mcp.server import mcp
from orion_mcp.tools import (
    TOOL_SAFETY_CLASSIFICATIONS,
    approve_recommendation,
    calculate_business_impact,
    execute_approved_action,
    get_anomaly_evidence,
    get_audit_events,
    get_business_anomalies,
    get_customer_analytics,
    get_inventory_analytics,
    get_investigation,
    get_marketing_analytics,
    get_recommendations,
    get_revenue_analytics,
    get_revenue_by_product,
    get_revenue_by_region,
    get_support_analytics,
    reject_recommendation,
    request_approval,
    start_investigation,
)


def test_mcp_tool_discovery():
    """Verify that all 18 required tools are defined and registered with safety classifications."""
    expected_tools = [
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
    ]

    assert len(expected_tools) == 18

    for tool_name in expected_tools:
        assert tool_name in TOOL_SAFETY_CLASSIFICATIONS, f"Tool {tool_name} missing classification"

    assert TOOL_SAFETY_CLASSIFICATIONS["get_business_anomalies"] == "READ_ONLY"
    assert TOOL_SAFETY_CLASSIFICATIONS["start_investigation"] == "ANALYSIS"
    assert TOOL_SAFETY_CLASSIFICATIONS["calculate_business_impact"] == "ANALYSIS"
    assert TOOL_SAFETY_CLASSIFICATIONS["get_recommendations"] == "PROPOSAL"
    assert TOOL_SAFETY_CLASSIFICATIONS["request_approval"] == "PROPOSAL"
    assert TOOL_SAFETY_CLASSIFICATIONS["approve_recommendation"] == "APPROVAL"
    assert TOOL_SAFETY_CLASSIFICATIONS["reject_recommendation"] == "APPROVAL"
    assert TOOL_SAFETY_CLASSIFICATIONS["execute_approved_action"] == "CONSEQUENTIAL_ACTION"


def test_mcp_read_only_tools():
    """Test all read-only analytics query tools."""
    # 1. get_business_anomalies
    anom_res = get_business_anomalies()
    assert "anomalies" in anom_res
    assert isinstance(anom_res["anomalies"], list)

    # 2. get_anomaly_evidence
    ev_res = get_anomaly_evidence("ANOM-REV-001")
    assert ev_res["anomaly_id"] == "ANOM-REV-001"
    assert "revenue" in ev_res
    assert "support" in ev_res
    assert "inventory" in ev_res

    # 3. get_revenue_analytics
    rev_res = get_revenue_analytics()
    assert "total_revenue" in rev_res

    # 4. get_revenue_by_region
    reg_res = get_revenue_by_region()
    assert "by_region" in reg_res

    # 5. get_revenue_by_product
    prod_res = get_revenue_by_product()
    assert "by_category" in prod_res

    # 6. get_customer_analytics
    cust_res = get_customer_analytics()
    assert "repeat_purchase_rate" in cust_res

    # 7. get_support_analytics
    supp_res = get_support_analytics()
    assert "summary" in supp_res

    # 8. get_inventory_analytics
    inv_res = get_inventory_analytics()
    assert "overall_stockout_rate" in inv_res

    # 9. get_marketing_analytics
    mktg_res = get_marketing_analytics()
    assert "summary" in mktg_res


def test_mcp_business_impact_calculation():
    """Test calculate_business_impact deterministic calculation tool."""
    impact = calculate_business_impact("ANOM-REV-001")
    assert impact["anomaly_id"] == "ANOM-REV-001"
    assert impact["realized_revenue_loss"] > 0
    assert impact["projected_30d_risk"] > 0
    assert impact["affected_customers_count"] > 0
    assert impact["severity"] == "critical"


def test_mcp_investigation_and_recommendations():
    """Test start_investigation and get_investigation tools."""
    inv_out = start_investigation("ANOM-REV-001")
    assert inv_out["investigation_id"].startswith("INV-")
    assert inv_out["confidence_score"] >= 0.8
    assert len(inv_out["root_causes"]) >= 2

    inv_id = inv_out["investigation_id"]
    inv_details = get_investigation(inv_id)
    assert inv_details["investigation_id"] == inv_id
    assert "root_causes" in inv_details
    assert "business_impact" in inv_details

    recs_out = get_recommendations(inv_id)
    assert "recommendations" in recs_out
    assert len(recs_out["recommendations"]) >= 1


def test_mcp_governance_rejection_and_unapproved_block():
    """Test human governance: unapproved action execution is blocked, rejection is enforced."""
    recs = get_recommendations()
    assert len(recs["recommendations"]) >= 2
    rec_target = recs["recommendations"][1]
    rec_id = rec_target["recommendation_id"]

    # 1. Attempt execute before approval -> must fail
    res = execute_approved_action(
        action_id=f"ACT-{rec_id}",
        approval_id=f"APPR-UNAPPROVED-{rec_id}",
    )
    assert res["status"] == "error"
    assert "EXECUTION_DENIED" in res["error"]

    # 2. Reject recommendation
    reject_res = reject_recommendation(
        recommendation_id=rec_id,
        approver="WarehouseOpsDirector",
        reason="Logistical resource constraint for expedited restock",
    )
    assert reject_res["status"] == "REJECTED"

    # 3. Attempt execute after rejection -> must fail
    res_after_reject = execute_approved_action(
        action_id=f"ACT-{rec_id}",
        approval_id=reject_res["approval_id"],
    )
    assert res_after_reject["status"] == "error"
    assert "EXECUTION_DENIED" in res_after_reject["error"]


def test_mcp_approval_and_safe_simulation():
    """Test full approval and safe action execution workflow."""
    recs = get_recommendations()
    assert len(recs["recommendations"]) >= 1
    rec = recs["recommendations"][0]
    rec_id = rec["recommendation_id"]

    # 1. Request approval
    req_res = request_approval(rec_id)
    assert req_res["status"] == "PENDING_APPROVAL"

    # 2. Approve recommendation
    appr_res = approve_recommendation(
        recommendation_id=rec_id,
        approver="ExecutiveOperationsVP",
        reason="Approved emergency customer support surge capacity",
    )
    assert appr_res["status"] == "APPROVED"
    approval_id = appr_res["approval_id"]

    # 3. Execute approved action
    exec_res = execute_approved_action(
        action_id=f"ACT-{rec_id}",
        approval_id=approval_id,
        parameters={"agents_to_add": 15},
    )
    assert exec_res["status"] == "success"
    assert exec_res["execution_mode"] == "SIMULATED ACTION"
    assert len(exec_res["result"]["changes_made"]) >= 1

    # 4. Attempt duplicate execution -> must fail
    dup_res = execute_approved_action(
        action_id=f"ACT-{rec_id}",
        approval_id=approval_id,
    )
    assert dup_res["status"] == "error"
    assert "EXECUTION_DENIED" in dup_res["error"]
    assert "already executed" in dup_res["error"] or "EXECUTED" in dup_res["error"]


def test_mcp_audit_trail():
    """Test get_audit_events tool."""
    audit_res = get_audit_events(limit=20)
    assert "audit_events" in audit_res
    assert audit_res["total_retrieved"] >= 1
    event_types = [ev["event_type"] for ev in audit_res["audit_events"]]
    assert any("ACTION" in et or "INVESTIGATION" in et or "APPROVAL" in et for et in event_types)
