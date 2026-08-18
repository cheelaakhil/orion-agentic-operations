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

from agents.runtime import global_agent_runtime
from agents.runtime.provider import AgentRunTrace

router = APIRouter(prefix="/agent-run", tags=["Agent Run Orchestration"])

# Track latest run id in memory
_latest_run_id: Optional[str] = None


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
