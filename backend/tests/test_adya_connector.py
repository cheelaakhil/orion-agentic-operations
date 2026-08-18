"""
ORION Milestone 6B: Adya Agent Runtime Adapter Test Suite

Verifies the integration boundary for the Adya AI Platform:
1. Tool discovery over provider interface
2. Multi-step autonomous investigation trace generation
3. Human approval gate enforcement
4. Rejection blocking action execution
5. Factory provider configuration
"""

import os
from agents.runtime.adya_runtime import AdyaAgentRuntime, AdyaConnectionMode
from agents.runtime.config import get_configured_agent_runtime
from agents.runtime.provider import AgentRunTrace, AgentRuntimeProvider


def test_adya_runtime_provider_interface():
    """Verify AdyaAgentRuntime adheres to AgentRuntimeProvider interface."""
    runtime = AdyaAgentRuntime(connection_mode=AdyaConnectionMode.SIMULATED_SSE)
    assert isinstance(runtime, AgentRuntimeProvider)
    assert "AdyaAgentRuntime" in runtime.get_provider_name()

    tools = runtime.discover_tools()
    assert isinstance(tools, dict)
    assert len(tools) == 18
    assert "get_business_anomalies" in tools
    assert "execute_approved_action" in tools


def test_adya_runtime_investigation_and_approval():
    """Verify Adya agent run up to human gate and through approved simulation."""
    runtime = AdyaAgentRuntime(connection_mode=AdyaConnectionMode.SIMULATED_SSE)
    trace = runtime.start_agent_run("ANOM-REV-001")

    assert isinstance(trace, AgentRunTrace)
    assert trace.run_id.startswith("ADYA-RUN-")
    assert trace.status == "WAITING_FOR_APPROVAL"
    assert trace.approval_status == "PENDING_APPROVAL"
    assert len(trace.steps) == 7

    # Verify Adya agent roles in trace
    adya_roles = [s.agent_role for s in trace.steps]
    assert "Adya Autonomous Executive" in adya_roles
    assert "Adya Data Extraction Agent" in adya_roles
    assert "Adya Causal Reasoning Engine" in adya_roles
    assert "Adya Governance Bridge" in adya_roles

    # Approve and execute
    rec_id = trace.active_recommendation_id
    completed_trace = runtime.approve_and_execute(
        run_id=trace.run_id,
        recommendation_id=rec_id,
        approver="AdyaExecutiveOperator",
        reason="Approved via Adya Integration Test Suite",
    )

    assert completed_trace.status == "COMPLETED"
    assert completed_trace.approval_status == "APPROVED"
    assert len(completed_trace.steps) == 10
    assert completed_trace.simulation_result is not None
    assert completed_trace.simulation_result.get("execution_mode") == "SIMULATED ACTION"


def test_adya_runtime_rejection_blocks_execution():
    """Verify that human rejection blocks Adya from executing consequential actions."""
    runtime = AdyaAgentRuntime(connection_mode=AdyaConnectionMode.SIMULATED_SSE)
    trace = runtime.start_agent_run("ANOM-REV-001")
    rec_id = trace.active_recommendation_id

    rejected_trace = runtime.reject_run(
        run_id=trace.run_id,
        recommendation_id=rec_id,
        rejector="AdyaExecutiveOperator",
        reason="Rejected due to operational budget ceiling",
    )

    assert rejected_trace.status == "REJECTED"
    assert rejected_trace.approval_status == "REJECTED"
    assert len(rejected_trace.steps) == 8


def test_runtime_factory_provider_selection():
    """Verify runtime factory creates appropriate provider based on config."""
    local_rt = get_configured_agent_runtime("local")
    assert local_rt.get_provider_name() == "ORION_LocalAgentRuntime_v1"

    adya_sim_rt = get_configured_agent_runtime("adya_simulated")
    assert "AdyaAgentRuntime_simulated_sse" in adya_sim_rt.get_provider_name()

    adya_live_rt = get_configured_agent_runtime("adya_live")
    assert "AdyaAgentRuntime_live_endpoint" in adya_live_rt.get_provider_name()
