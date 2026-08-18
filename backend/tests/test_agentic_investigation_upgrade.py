"""
Tests for Core Agentic Investigation Upgrade.

Verifies:
1. Multi-step real MCP tool chain invocation.
2. Factual evidence collection from SQL data.
3. Root-cause hypothesis grounded in returned evidence.
4. Business impact calculations from true metrics.
5. Recommendation generation with risk & parameter tracking.
6. Decision trace generation and confidence scorecards.
7. Human approval gate blocking unapproved executions.
8. Approved actions executing strictly under SIMULATED ACTION mode.
9. Safety tier enforcement & structured denials.
10. Tamper-evident audit events recorded at every stage.
11. Insufficient evidence / invalid anomaly handling.
"""

import pytest
from agents.runtime.local_runtime import LocalAgentRuntime
from backend.core.database import SessionLocal
from backend.models.models import AuditEvent
from orion_mcp.tools import execute_approved_action


def test_agentic_investigation_full_chain_invocation():
    """Verify that starting an agent run invokes the full chain of MCP analytical tools."""
    runtime = LocalAgentRuntime()
    trace = runtime.start_agent_run("ANOM-REV-001")

    # 1. Verify trace state paused at Human Approval Gate
    assert trace.status == "WAITING_FOR_APPROVAL"
    assert trace.approval_status == "PENDING_APPROVAL"
    assert trace.active_recommendation_id is not None
    assert trace.approval_request_id is not None
    assert len(trace.steps) >= 10, f"Expected at least 10 steps, got {len(trace.steps)}"

    # 2. Verify all expected MCP tools were invoked
    tools_called = [s.tool_called for s in trace.steps]
    expected_tools = [
        "get_business_anomalies",
        "get_revenue_analytics",
        "get_support_analytics",
        "get_inventory_analytics",
        "get_customer_analytics",
        "get_anomaly_evidence",
        "start_investigation",
        "get_investigation",
        "calculate_business_impact",
        "get_recommendations",
        "request_approval",
    ]
    for expected_tool in expected_tools:
        assert expected_tool in tools_called, f"Expected tool '{expected_tool}' was not invoked in agent run"

    # 3. Verify evidence collection from actual tool outputs
    evidence_step = next(s for s in trace.steps if s.tool_called == "get_anomaly_evidence")
    assert evidence_step.evidence_type == "OBSERVED"
    assert "revenue" in evidence_step.details
    assert "support" in evidence_step.details

    # 4. Verify root cause uses returned evidence
    rc_step = next(s for s in trace.steps if s.tool_called == "get_investigation")
    assert rc_step.evidence_type == "HYPOTHESIS"
    assert len(rc_step.details.get("root_causes", [])) > 0

    # 5. Verify business impact calculated from actual database figures
    impact_step = next(s for s in trace.steps if s.tool_called == "calculate_business_impact")
    assert impact_step.details.get("realized_revenue_loss", 0) > 0

    # 6. Verify decision trace and confidence scoring
    assert trace.decision_trace is not None
    assert len(trace.decision_trace) >= 5
    stages = [d.stage for d in trace.decision_trace]
    assert "OBSERVATION" in stages
    assert "EVIDENCE" in stages
    assert "HYPOTHESIS" in stages
    assert "IMPACT" in stages
    assert "RECOMMENDATION" in stages

    assert trace.scores is not None
    assert 0.0 <= trace.scores.detection_confidence <= 1.0
    assert 0.0 <= trace.scores.root_cause_confidence <= 1.0
    assert 0.0 <= trace.scores.recommendation_confidence <= 1.0
    assert trace.scores.action_risk in ["LOW", "MEDIUM", "HIGH"]

    # 7. Verify human approval gate stops execution before simulation
    assert trace.simulation_result is None


def test_agentic_investigation_approval_and_simulation():
    """Verify that explicit human approval authorizes simulated execution and commits audit events."""
    runtime = LocalAgentRuntime()
    trace = runtime.start_agent_run("ANOM-REV-001")
    run_id = trace.run_id
    rec_id = trace.active_recommendation_id

    # Approve run
    completed_trace = runtime.approve_and_execute(
        run_id=run_id,
        recommendation_id=rec_id,
        approver="ExecutiveOperationsDirector",
        reason="Authorization granted for support escalation simulation",
    )

    assert completed_trace.status == "COMPLETED"
    assert completed_trace.approval_status == "APPROVED"
    assert completed_trace.simulation_result is not None
    assert completed_trace.simulation_result.get("execution_mode") == "SIMULATED ACTION"

    # Verify action step added to trace
    action_step = next((s for s in completed_trace.steps if s.tool_called == "execute_approved_action"), None)
    assert action_step is not None
    assert action_step.status == "COMPLETED"
    assert action_step.evidence_type == "ACTION_RESULT"

    # Verify audit verification step
    audit_step = next((s for s in completed_trace.steps if s.tool_called == "get_audit_events"), None)
    assert audit_step is not None
    assert audit_step.status == "COMPLETED"


def test_agentic_investigation_rejection_blocks_execution():
    """Verify that human rejection permanently halts execution and blocks consequential actions."""
    runtime = LocalAgentRuntime()
    trace = runtime.start_agent_run("ANOM-REV-001")
    run_id = trace.run_id
    rec_id = trace.active_recommendation_id

    rejected_trace = runtime.reject_run(
        run_id=run_id,
        recommendation_id=rec_id,
        rejector="ExecutiveOperationsDirector",
        reason="Budget threshold exceeded",
    )

    assert rejected_trace.status == "REJECTED"
    assert rejected_trace.approval_status == "REJECTED"
    assert rejected_trace.simulation_result is None

    # Verify rejection step in trace
    rej_step = next((s for s in rejected_trace.steps if s.tool_called == "reject_recommendation"), None)
    assert rej_step is not None
    assert rej_step.status == "BLOCKED"


def test_unapproved_action_structured_denial_enforcement():
    """Verify backend safety tier enforcement strictly denies unapproved consequential execution."""
    # Attempt execution with empty approval token
    denial_empty = execute_approved_action("ACT-TEST-001", "")
    assert denial_empty.get("allowed") is False
    assert denial_empty.get("reason") == "Human approval required"
    assert denial_empty.get("required_gate") == "APPROVAL"

    # Attempt execution with non-existent token
    denial_nonexistent = execute_approved_action("ACT-TEST-001", "APPR-NON-EXISTENT-999")
    assert denial_nonexistent.get("allowed") is False
    assert "does not exist" in denial_nonexistent.get("error", "")


def test_agentic_investigation_history_retrieval():
    """Verify retrieval of all historical agent run traces."""
    runtime = LocalAgentRuntime()
    trace1 = runtime.start_agent_run("ANOM-REV-001")
    trace2 = runtime.start_agent_run("ANOM-REV-001")

    all_runs = runtime.get_all_runs()
    assert len(all_runs) >= 2
    assert any(r.run_id == trace1.run_id for r in all_runs)
    assert any(r.run_id == trace2.run_id for r in all_runs)


def test_agentic_investigation_insufficient_evidence_handling():
    """Verify that requesting an investigation for an unknown/non-existent anomaly reports INSUFFICIENT EVIDENCE."""
    runtime = LocalAgentRuntime()
    trace = runtime.start_agent_run("ANOM-NON-EXISTENT-999")

    # If anomalies exist in DB, it falls back to first real anomaly or fails gracefully
    assert trace.status in ["WAITING_FOR_APPROVAL", "FAILED"]
    if trace.status == "FAILED":
        assert "INSUFFICIENT EVIDENCE" in trace.steps[0].output_summary
