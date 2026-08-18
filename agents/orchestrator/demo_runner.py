"""
ORION Milestone 6A: Agentic Demonstration Orchestrator

Runs the complete 13-step deterministic autonomous investigation workflow
using ORION's provider-agnostic LocalAgentRuntime.
"""

import sys
from datetime import datetime
from agents.runtime import global_agent_runtime


def run_agentic_demo(anomaly_id: str = "ANOM-REV-001"):
    print("==================================================================")
    print("      ORION AGENTIC ORCHESTRATION DEMO (MILESTONE 6A)            ")
    print("==================================================================\n")

    runtime = global_agent_runtime

    print(f"[*] Runtime Provider: {runtime.get_provider_name()}")
    print("[*] Discovering MCP Tools...")
    tools = runtime.discover_tools()
    print(f"    Discovered {len(tools)} tools across 5 safety tiers.\n")

    print(f"[*] Initiating Autonomous Multi-Agent Investigation for {anomaly_id}...")
    trace = runtime.start_agent_run(anomaly_id)

    print("\n--- AGENT EXECUTION TRACE (PHASE 1: UP TO HUMAN GATE) ---")
    for s in trace.steps:
        print(f"[{s.step_id:02d}] {s.agent_role:<25} | Tool: {s.tool_called:<26} | Status: {s.status}")
        print(f"     Type: [{s.evidence_type or 'INFO'}] Duration: {s.duration_ms}ms")
        print(f"     Output: {s.output_summary}\n")

    print("+-------------------------------------------------------------+")
    print("|                 HUMAN APPROVAL REQUIRED                     |")
    print("|                                                             |")
    print(f"| Recommendation ID: {trace.active_recommendation_id:<41}|")
    print(f"| Approval Status:   {trace.approval_status:<41}|")
    print("| Governance Action:  [ APPROVE ]       [ REJECT ]            |")
    print("+-------------------------------------------------------------+\n")

    rec_id = trace.active_recommendation_id or "REC-001"
    print(f"[*] Human Executive Approves Recommendation: {rec_id}...")
    completed_trace = runtime.approve_and_execute(
        run_id=trace.run_id,
        recommendation_id=rec_id,
        approver="ChiefOperationsOfficer",
        reason="Approved emergency tier-1 support capacity expansion via Agentic Supervisor",
    )

    print("\n--- AGENT EXECUTION TRACE (PHASE 2: EXECUTION & AUDIT) ---")
    for s in completed_trace.steps[7:]:
        print(f"[{s.step_id:02d}] {s.agent_role:<25} | Tool: {s.tool_called:<26} | Status: {s.status}")
        print(f"     Type: [{s.evidence_type or 'INFO'}] Duration: {s.duration_ms}ms")
        print(f"     Output: {s.output_summary}\n")

    print("==================================================================")
    print(f"  DEMO RUN COMPLETE: Run ID = {completed_trace.run_id}")
    print(f"  Final Status: {completed_trace.status} | Total Steps: {len(completed_trace.steps)}")
    print("==================================================================")

    return completed_trace


if __name__ == "__main__":
    anom_target = sys.argv[1] if len(sys.argv) > 1 else "ANOM-REV-001"
    run_agentic_demo(anom_target)
