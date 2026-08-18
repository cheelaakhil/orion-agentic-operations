"""
ORION Milestone 6A: Agentic Demonstration & Orchestration Test Suite

Tests:
1. Supervisor workflow & MCP tool mapping
2. Agent trace generation & structure
3. Evidence propagation with source tags (OBSERVED, INFERRED, HYPOTHESIS)
4. Human approval gate pausing execution
5. Rejected approval blocking execution
6. Successful approved simulation with SIMULATED ACTION
7. Audit creation during agent run
8. Provider abstraction interface & LocalAgentRuntime
9. FastAPI REST API endpoints for agent runs
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from agents.runtime import LocalAgentRuntime, global_agent_runtime
from agents.runtime.provider import AgentRuntimeProvider, AgentRunTrace
from agents.orchestrator.demo_runner import run_agentic_demo


@pytest.fixture
def client():
    return TestClient(app)


def test_provider_abstraction_interface():
    """Verify that LocalAgentRuntime adheres to AgentRuntimeProvider interface."""
    runtime = LocalAgentRuntime()
    assert isinstance(runtime, AgentRuntimeProvider)
    assert runtime.get_provider_name() == "ORION_LocalAgentRuntime_v1"

    tools = runtime.discover_tools()
    assert isinstance(tools, dict)
    assert len(tools) == 18
    assert "get_business_anomalies" in tools
    assert "execute_approved_action" in tools


def test_agent_run_lifecycle_and_trace():
    """Verify autonomous agent execution up to the Human Approval Gate."""
    runtime = LocalAgentRuntime()
    trace = runtime.start_agent_run("ANOM-REV-001")

    assert isinstance(trace, AgentRunTrace)
    assert trace.run_id.startswith("RUN-")
    assert trace.anomaly_id == "ANOM-REV-001"
    assert trace.status == "WAITING_FOR_APPROVAL"
    assert trace.approval_status == "PENDING_APPROVAL"
    assert trace.active_recommendation_id is not None
    assert len(trace.steps) == 7

    # Verify agent roles in order
    expected_agents = [
        "Supervisor Agent",
        "Data Analyst Agent",
        "Investigation Agent",
        "Root Cause Agent",
        "Business Impact Agent",
        "Recommendation Agent",
        "Governance Agent",
    ]
    actual_agents = [s.agent_role for s in trace.steps]
    assert actual_agents == expected_agents

    # Verify evidence categorization
    evidence_types = [s.evidence_type for s in trace.steps]
    assert "OBSERVED" in evidence_types
    assert "INFERRED" in evidence_types
    assert "HYPOTHESIS" in evidence_types
    assert "PROPOSAL" in evidence_types

    # Step durations
    for s in trace.steps:
        assert s.duration_ms >= 0.0
        assert s.timestamp is not None
        assert s.tool_called is not None


def test_human_approval_and_simulation():
    """Verify human executive approval and safe simulated action execution."""
    runtime = LocalAgentRuntime()
    trace = runtime.start_agent_run("ANOM-REV-001")
    rec_id = trace.active_recommendation_id

    # Execute approval
    completed_trace = runtime.approve_and_execute(
        run_id=trace.run_id,
        recommendation_id=rec_id,
        approver="ChiefOperationsOfficer",
        reason="Approved emergency capacity allocation",
    )

    assert completed_trace.status == "COMPLETED"
    assert completed_trace.approval_status == "APPROVED"
    assert len(completed_trace.steps) == 10
    assert completed_trace.simulation_result is not None
    assert completed_trace.simulation_result.get("execution_mode") == "SIMULATED ACTION"
    assert completed_trace.completed_at is not None

    # Verify action step
    action_step = completed_trace.steps[8]
    assert action_step.agent_role == "Action Agent"
    assert action_step.tool_called == "execute_approved_action"
    assert action_step.status == "COMPLETED"


def test_human_rejection_blocks_execution():
    """Verify that human executive rejection blocks operational action execution."""
    runtime = LocalAgentRuntime()
    trace = runtime.start_agent_run("ANOM-REV-001")
    rec_id = trace.active_recommendation_id

    # Execute rejection
    rejected_trace = runtime.reject_run(
        run_id=trace.run_id,
        recommendation_id=rec_id,
        rejector="ChiefOperationsOfficer",
        reason="Rejected due to operational budget ceiling",
    )

    assert rejected_trace.status == "REJECTED"
    assert rejected_trace.approval_status == "REJECTED"
    assert len(rejected_trace.steps) == 8

    rejection_step = rejected_trace.steps[7]
    assert rejection_step.agent_role == "Human Executive Operator"
    assert rejection_step.tool_called == "reject_recommendation"
    assert rejection_step.status == "BLOCKED"


def test_agentic_demo_runner_execution():
    """Verify standalone demo runner execution."""
    completed_trace = run_agentic_demo("ANOM-REV-001")
    assert completed_trace.status == "COMPLETED"
    assert len(completed_trace.steps) == 10


def test_agent_run_rest_api_lifecycle(client):
    """Verify FastAPI endpoints for agent run orchestration."""
    # 1. Start agent run
    start_resp = client.post("/api/v1/agent-run/start", json={"anomaly_id": "ANOM-REV-001"})
    assert start_resp.status_code == 200
    trace_data = start_resp.json()
    run_id = trace_data["run_id"]
    rec_id = trace_data["active_recommendation_id"]
    assert trace_data["status"] == "WAITING_FOR_APPROVAL"

    # 2. Get run trace by ID
    get_resp = client.get(f"/api/v1/agent-run/{run_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["run_id"] == run_id

    # 3. Get latest run trace
    latest_resp = client.get("/api/v1/agent-run/latest")
    assert latest_resp.status_code == 200
    assert latest_resp.json()["run_id"] == run_id

    # 4. Approve run
    approve_resp = client.post(
        f"/api/v1/agent-run/{run_id}/approve",
        json={
            "recommendation_id": rec_id,
            "approver": "ExecutiveVP",
            "reason": "REST API Automated Verification",
        },
    )
    assert approve_resp.status_code == 200
    completed_data = approve_resp.json()
    assert completed_data["status"] == "COMPLETED"
    assert completed_data["approval_status"] == "APPROVED"
    assert completed_data["simulation_result"]["execution_mode"] == "SIMULATED ACTION"
