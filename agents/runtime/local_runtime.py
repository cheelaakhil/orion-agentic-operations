"""
ORION Local Agent Runtime Implementation

Implements the AgentRuntimeProvider interface using ORION's verified MCP business
tool layer and deterministic analytics engine.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from agents.runtime.provider import AgentRunTrace, AgentRuntimeProvider, AgentTraceStep
from orion_mcp.tools import (
    TOOL_SAFETY_CLASSIFICATIONS,
    approve_recommendation,
    calculate_business_impact,
    execute_approved_action,
    get_anomaly_evidence,
    get_audit_events,
    get_business_anomalies,
    get_investigation,
    get_recommendations,
    reject_recommendation,
    request_approval,
    start_investigation,
)


class LocalAgentRuntime(AgentRuntimeProvider):
    """
    Provider-agnostic local implementation of ORION's agentic workflow coordinator.

    Orchestrates the logical agent pipeline:
    1. Supervisor Agent (anomaly detection & goal formulation)
    2. Data Analyst Agent (quantitative multi-dimensional evidence extraction)
    3. Investigation Agent (causal pipeline execution)
    4. Root Cause Agent (hypothesis validation & temporal isolation)
    5. Business Impact Agent (deterministic financial impact calculation)
    6. Recommendation Agent (prioritized remediation proposal generation)
    7. Governance Agent (human authorization request creation)
    8. Human Operator Gate (interactive approval / rejection pause)
    9. Action Agent (safe operational simulation under SIMULATED ACTION mode)
    10. Audit Agent (operations trail logging & verification)
    """

    def __init__(self):
        self._runs: Dict[str, AgentRunTrace] = {}

    def get_provider_name(self) -> str:
        return "ORION_LocalAgentRuntime_v1"

    def discover_tools(self) -> Dict[str, str]:
        return TOOL_SAFETY_CLASSIFICATIONS.copy()

    def start_agent_run(self, anomaly_id: str = "ANOM-REV-001") -> AgentRunTrace:
        """
        Executes Steps 1 through 9 of the investigation workflow and pauses at the
        mandatory Human Approval Gate.
        """
        run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
        start_time = datetime.now(timezone.utc).isoformat()
        steps = []
        step_idx = 1

        trace = AgentRunTrace(
            run_id=run_id,
            anomaly_id=anomaly_id,
            status="RUNNING",
            started_at=start_time,
            steps=[],
        )
        self._runs[run_id] = trace

        # -------------------------------------------------------------
        # STEP 1: Supervisor Agent — Detect Critical Business Anomalies
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        anom_res = get_business_anomalies()
        t1 = time.perf_counter()
        anomalies = anom_res.get("anomalies", [])
        target_anom = next((a for a in anomalies if a["anomaly_id"] == anomaly_id), None)
        if not target_anom and anomalies:
            target_anom = anomalies[0]
            anomaly_id = target_anom["anomaly_id"]
            trace.anomaly_id = anomaly_id

        steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Supervisor Agent",
                tool_called="get_business_anomalies",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["get_business_anomalies"],
                input_summary="Query all active business metric anomalies across revenue, support, inventory, marketing.",
                output_summary=f"Discovered {len(anomalies)} anomalies. Selected critical target '{anomaly_id}' ({target_anom['metric'] if target_anom else 'N/A'}: {target_anom.get('change_percentage', 0):.1f}%).",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="OBSERVED",
                details={"anomaly": target_anom},
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 2: Data Analyst Agent — Extract Quantitative Evidence
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        evidence_res = get_anomaly_evidence(anomaly_id)
        t1 = time.perf_counter()

        rev_change = evidence_res.get("revenue", {}).get("change_percentage", 0)
        sla_breach = evidence_res.get("support", {}).get("evaluation_sla_breach_rate", 0)
        elec_stockout = evidence_res.get("inventory", {}).get("stockout_rate_by_category", {}).get("Electronics", 0)

        steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Data Analyst Agent",
                tool_called="get_anomaly_evidence",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["get_anomaly_evidence"],
                input_summary=f"Extract baseline vs evaluation multi-dimensional metrics for {anomaly_id}.",
                output_summary=f"Observed: Revenue change {rev_change}%, Support SLA breach rate {sla_breach*100:.1f}%, Electronics stockout rate {elec_stockout*100:.1f}%.",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="OBSERVED",
                details=evidence_res,
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 3: Investigation Agent — Trigger Multi-Agent Pipeline
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        inv_start_res = start_investigation(anomaly_id)
        t1 = time.perf_counter()
        inv_id = inv_start_res.get("investigation_id")

        steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Investigation Agent",
                tool_called="start_investigation",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["start_investigation"],
                input_summary=f"Orchestrate causal hypothesis formulation and fact classification for {anomaly_id}.",
                output_summary=f"Investigation {inv_id} completed with confidence {inv_start_res.get('confidence_score', 0):.0%}. Formulated root causes.",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="INFERRED",
                details=inv_start_res,
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 4: Root Cause Agent — Retrieve Causal Hypotheses
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        inv_details = get_investigation(inv_id)
        t1 = time.perf_counter()
        root_causes = inv_details.get("root_causes", [])
        primary_rc = root_causes[0]["description"] if root_causes else "Multi-factor operational bottleneck"

        steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Root Cause Agent",
                tool_called="get_investigation",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["get_investigation"],
                input_summary=f"Fetch ranked causal hypotheses and timeline steps for {inv_id}.",
                output_summary=f"Identified {len(root_causes)} ranked root causes. Primary hypothesis: {primary_rc[:100]}...",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="HYPOTHESIS",
                details={"root_causes": root_causes},
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 5: Business Impact Agent — Calculate Grounded Financial Loss
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        impact_res = calculate_business_impact(anomaly_id)
        t1 = time.perf_counter()
        realized_loss = impact_res.get("realized_revenue_loss", 0.0)
        risk_30d = impact_res.get("projected_30d_risk", 0.0)
        affected_cust = impact_res.get("affected_customers_count", 0)

        steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Business Impact Agent",
                tool_called="calculate_business_impact",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["calculate_business_impact"],
                input_summary=f"Quantify realized historical loss and 30d/90d forward revenue risk for {anomaly_id}.",
                output_summary=f"Calculated: Realized Loss ${realized_loss:,.2f}, 30-Day Forward Risk ${risk_30d:,.2f}, Affected Accounts {affected_cust}.",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="OBSERVED",
                details=impact_res,
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 6: Recommendation Agent — Retrieve Ranked Interventions
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        recs_res = get_recommendations(inv_id)
        t1 = time.perf_counter()
        recommendations = recs_res.get("recommendations", [])
        target_rec = recommendations[0] if recommendations else None
        target_rec_id = target_rec["recommendation_id"] if target_rec else "REC-001"

        steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Recommendation Agent",
                tool_called="get_recommendations",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["get_recommendations"],
                input_summary=f"Fetch actionable, prioritized remediations for investigation {inv_id}.",
                output_summary=f"Generated {len(recommendations)} recommendations. Top priority candidate: {target_rec_id} ({target_rec.get('title', 'Remediation') if target_rec else ''}).",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="PROPOSAL",
                details={"recommendations": recommendations},
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 7: Governance Agent — Request Human Authorization
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        approval_res = request_approval(target_rec_id)
        t1 = time.perf_counter()
        approval_id = approval_res.get("approval_id")

        steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Governance Agent",
                tool_called="request_approval",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["request_approval"],
                input_summary=f"Create formal authorization request for {target_rec_id}.",
                output_summary=f"Authorization request {approval_id} registered with status 'PENDING_APPROVAL'. Pausing workflow at Human Approval Gate.",
                status="WAITING_FOR_APPROVAL",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="PROPOSAL",
                details=approval_res,
            )
        )

        trace.steps = steps
        trace.status = "WAITING_FOR_APPROVAL"
        trace.active_recommendation_id = target_rec_id
        trace.approval_request_id = approval_id
        trace.approval_status = "PENDING_APPROVAL"

        return trace

    def approve_and_execute(
        self,
        run_id: str,
        recommendation_id: str,
        approver: str = "ExecutiveOperationsVP",
        reason: str = "Approved via Executive Operations Console",
    ) -> AgentRunTrace:
        """
        Processes human executive approval and executes the safe operational simulation.
        """
        trace = self._runs.get(run_id)
        if not trace:
            raise ValueError(f"Agent run '{run_id}' not found.")

        step_idx = len(trace.steps) + 1

        # -------------------------------------------------------------
        # STEP 8: Human Approval Authorized
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        appr_res = approve_recommendation(
            recommendation_id=recommendation_id,
            approver=approver,
            reason=reason,
        )
        t1 = time.perf_counter()
        approval_id = appr_res.get("approval_id")

        trace.steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Human Executive Operator",
                tool_called="approve_recommendation",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["approve_recommendation"],
                input_summary=f"Human authorization granted for {recommendation_id} by {approver}. Reason: '{reason}'.",
                output_summary=f"Approval status APPROVED. Issued execution authorization token {approval_id}.",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="ACTION_RESULT",
                details=appr_res,
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 9: Action Agent — Execute Safe Operational Simulation
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        action_id = f"ACT-{recommendation_id}"
        exec_res = execute_approved_action(
            action_id=action_id,
            approval_id=approval_id,
            parameters={"agents_to_add": 15},
        )
        t1 = time.perf_counter()

        trace.steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Action Agent",
                tool_called="execute_approved_action",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["execute_approved_action"],
                input_summary=f"Execute approved operational simulation for {action_id} with token {approval_id}.",
                output_summary=f"Execution completed in '{exec_res.get('execution_mode', 'SIMULATED ACTION')}'. Applied {len(exec_res.get('result', {}).get('changes_made', []))} simulated configuration adjustments.",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="ACTION_RESULT",
                details=exec_res,
            )
        )
        step_idx += 1

        # -------------------------------------------------------------
        # STEP 10: Audit Agent — Retrieve Immutable Audit Log
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        audit_res = get_audit_events(limit=6)
        t1 = time.perf_counter()

        trace.steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Audit Agent",
                tool_called="get_audit_events",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["get_audit_events"],
                input_summary="Verify full operational audit trail across lifecycle.",
                output_summary=f"Confirmed {audit_res.get('total_retrieved', 0)} recent audit events committed to immutable log.",
                status="COMPLETED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="OBSERVED",
                details={"audit_events_count": audit_res.get("total_retrieved", 0)},
            )
        )

        trace.status = "COMPLETED"
        trace.approval_status = "APPROVED"
        trace.simulation_result = exec_res
        trace.completed_at = datetime.now(timezone.utc).isoformat()

        return trace

    def reject_run(
        self,
        run_id: str,
        recommendation_id: str,
        rejector: str = "ExecutiveOperationsVP",
        reason: str = "Rejected during executive review",
    ) -> AgentRunTrace:
        """
        Processes human executive rejection, permanently blocking operational execution.
        """
        trace = self._runs.get(run_id)
        if not trace:
            raise ValueError(f"Agent run '{run_id}' not found.")

        step_idx = len(trace.steps) + 1

        t0 = time.perf_counter()
        rej_res = reject_recommendation(
            recommendation_id=recommendation_id,
            approver=rejector,
            reason=reason,
        )
        t1 = time.perf_counter()

        trace.steps.append(
            AgentTraceStep(
                step_id=step_idx,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_role="Human Executive Operator",
                tool_called="reject_recommendation",
                tool_safety=TOOL_SAFETY_CLASSIFICATIONS["reject_recommendation"],
                input_summary=f"Human rejection executed for {recommendation_id} by {rejector}. Reason: '{reason}'.",
                output_summary="Approval status REJECTED. Downstream action execution permanently blocked.",
                status="BLOCKED",
                duration_ms=round((t1 - t0) * 1000, 2),
                evidence_type="ACTION_RESULT",
                details=rej_res,
            )
        )

        trace.status = "REJECTED"
        trace.approval_status = "REJECTED"
        trace.completed_at = datetime.now(timezone.utc).isoformat()

        return trace

    def get_run_trace(self, run_id: str) -> Optional[AgentRunTrace]:
        return self._runs.get(run_id)
