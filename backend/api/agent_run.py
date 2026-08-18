"""
ORION Agentic Run REST API Router

Exposes the provider-agnostic AgentRuntimeProvider lifecycle to the frontend:
- POST /api/v1/agent-run/start
- GET  /api/v1/agent-run/{run_id}
- POST /api/v1/agent-run/{run_id}/approve
- POST /api/v1/agent-run/{run_id}/reject
- GET  /api/v1/agent-run/latest
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.config import settings
from agents.runtime import global_agent_runtime
from agents.runtime.provider import AgentRunTrace

router = APIRouter(prefix="/agent-run", tags=["Agent Run Orchestration"])

# Track latest run id in memory
_latest_run_id: Optional[str] = None

MCP_TOOLS_CATALOG = [
    {
        "name": "get_business_anomalies",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Scans operations data to detect statistical outliers across revenue, support, inventory, and marketing.",
    },
    {
        "name": "get_anomaly_evidence",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Retrieves multi-dimensional factual evidence package for a detected anomaly.",
    },
    {
        "name": "get_revenue_analytics",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Calculates revenue KPIs, daily timeseries trends, and pre/post incident performance.",
    },
    {
        "name": "get_revenue_by_product",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Breaks down sales performance by product category to identify isolated drops.",
    },
    {
        "name": "get_revenue_by_region",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Provides geographic distribution of sales and conversion rates.",
    },
    {
        "name": "get_customer_analytics",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Analyzes repeat purchase behavior, customer cohorts, and churn rates.",
    },
    {
        "name": "get_support_analytics",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Computes support queue volume, average resolution time, SLA breach rate, and CSAT.",
    },
    {
        "name": "get_inventory_analytics",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Evaluates warehouse stock levels, stockout rates by category, and replenishment lead times.",
    },
    {
        "name": "get_marketing_analytics",
        "category": "Deterministic Analytics",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Quantifies ad spend, CTR, conversion rates, and ROAS across marketing campaigns.",
    },
    {
        "name": "start_investigation",
        "category": "Multi-Agent Investigation",
        "safety_tier": "ANALYSIS",
        "requires_approval": False,
        "description": "Initiates autonomous multi-agent causal investigation pipeline over an anomaly.",
    },
    {
        "name": "get_investigation",
        "category": "Multi-Agent Investigation",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Retrieves ranked causal hypotheses with confidence scores and supporting evidence.",
    },
    {
        "name": "calculate_business_impact",
        "category": "Business Impact Modeling",
        "safety_tier": "ANALYSIS",
        "requires_approval": False,
        "description": "Calculates deterministic cumulative financial loss, daily burn rate, and counterfactual recovery.",
    },
    {
        "name": "get_recommendations",
        "category": "Action Recommendations",
        "safety_tier": "PROPOSAL",
        "requires_approval": False,
        "description": "Retrieves prioritized, actionable operational remediations with projected ROI.",
    },
    {
        "name": "request_approval",
        "category": "Governance Gate",
        "safety_tier": "PROPOSAL",
        "requires_approval": False,
        "description": "Submits a recommendation to the human executive approval queue and returns an approval request ID.",
    },
    {
        "name": "approve_recommendation",
        "category": "Governance Gate",
        "safety_tier": "APPROVAL",
        "requires_approval": False,
        "description": "Records human executive approval in the database registry and issues an execution authorization token.",
    },
    {
        "name": "reject_recommendation",
        "category": "Governance Gate",
        "safety_tier": "APPROVAL",
        "requires_approval": False,
        "description": "Records human executive rejection in the database registry, permanently blocking action execution.",
    },
    {
        "name": "execute_approved_action",
        "category": "Safe Action Execution",
        "safety_tier": "CONSEQUENT_ACTION",
        "requires_approval": True,
        "description": "Verifies valid authorization token and executes safe domain action simulation with rollback tracking.",
    },
    {
        "name": "get_audit_events",
        "category": "Audit & Compliance",
        "safety_tier": "READ_ONLY",
        "requires_approval": False,
        "description": "Queries the tamper-evident operations audit trail for compliance and post-mortem analysis.",
    },
]


@router.get("/runtime-info")
def get_runtime_info():
    """Returns metadata regarding active AgentRuntimeProvider and Adya integration status."""
    return {
        "active_provider": settings.agent_provider,
        "adya_adapter_status": "ADAPTER-READY ONLY (Interface implemented, not live-connected)",
        "total_mcp_tools": len(MCP_TOOLS_CATALOG),
        "safety_model_tiers": [
            "READ_ONLY",
            "ANALYSIS",
            "PROPOSAL",
            "APPROVAL",
            "CONSEQUENT_ACTION (Requires Human Approval)",
        ],
        "governance_guarantee": "Human approval strictly enforced; unapproved action returns EXECUTION_DENIED",
        "execution_mode": "SIMULATED ACTION",
    }


@router.get("/mcp-tools")
def list_mcp_tools():
    """Returns the comprehensive catalog of 18 MCP tools exposed by the ORION FastMCP Server."""
    return {"tools": MCP_TOOLS_CATALOG, "count": len(MCP_TOOLS_CATALOG)}


class StartAgentRunRequest(BaseModel):
    anomaly_id: str = Field(default="ANOM-REV-001", description="Target anomaly identifier")


class ApproveAgentRunRequest(BaseModel):
    recommendation_id: str = Field(..., description="Recommendation to approve")
    approver: str = Field(default="ChiefOperationsOfficer", description="Name of approving executive")
    reason: str = Field(default="Approved via Executive Operations Console", description="Approval justification")


class RejectAgentRunRequest(BaseModel):
    recommendation_id: str = Field(..., description="Recommendation to reject")
    rejector: str = Field(default="ChiefOperationsOfficer", description="Name of rejecting executive")
    reason: str = Field(default="Rejected during executive review", description="Rejection reason")


@router.post("/start", response_model=AgentRunTrace)
def start_agent_run(req: StartAgentRunRequest):
    """
    Initiates an autonomous multi-agent run using the AgentRuntimeProvider.
    Executes through anomaly detection, evidence gathering, investigation, impact calculation,
    and recommendation generation, pausing at the Human Approval Gate.
    """
    global _latest_run_id
    try:
        trace = global_agent_runtime.start_agent_run(req.anomaly_id)
        _latest_run_id = trace.run_id
        return trace
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent run: {str(e)}")


@router.get("/latest", response_model=Optional[AgentRunTrace])
def get_latest_agent_run():
    """Retrieves the most recent agent run trace."""
    global _latest_run_id
    if not _latest_run_id:
        # If no run exists, automatically trigger one for ANOM-REV-001 so the dashboard is immediately populated
        trace = global_agent_runtime.start_agent_run("ANOM-REV-001")
        _latest_run_id = trace.run_id
        return trace
    trace = global_agent_runtime.get_run_trace(_latest_run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="No active agent run found")
    return trace


@router.get("/{run_id}", response_model=AgentRunTrace)
def get_agent_run(run_id: str):
    """Retrieves a specific agent run trace by its ID."""
    trace = global_agent_runtime.get_run_trace(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Agent run '{run_id}' not found")
    return trace


@router.post("/{run_id}/approve", response_model=AgentRunTrace)
def approve_agent_run(run_id: str, req: ApproveAgentRunRequest):
    """
    Provides human authorization to resume an agent run from the approval gate,
    executing the safe operational simulation and committing audit events.
    """
    try:
        trace = global_agent_runtime.approve_and_execute(
            run_id=run_id,
            recommendation_id=req.recommendation_id,
            approver=req.approver,
            reason=req.reason,
        )
        return trace
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval execution failed: {str(e)}")


@router.post("/{run_id}/reject", response_model=AgentRunTrace)
def reject_agent_run(run_id: str, req: RejectAgentRunRequest):
    """
    Rejects the proposed recommendation, permanently blocking action execution and logging
    the rejection to the immutable audit trail.
    """
    try:
        trace = global_agent_runtime.reject_run(
            run_id=run_id,
            recommendation_id=req.recommendation_id,
            rejector=req.rejector,
            reason=req.reason,
        )
        return trace
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rejection processing failed: {str(e)}")
