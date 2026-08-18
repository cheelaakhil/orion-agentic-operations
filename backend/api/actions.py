"""
ORION Safe Action Execution REST API Endpoints.

Enforces human-in-the-loop authorization gates before executing safe operational simulations.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.implementations.local.action import LocalActionAgent
from agents.interfaces.action import ActionInput, ActionType
from backend.core.database import get_db
from backend.models.models import ApprovalRequestModel, RecommendationModel

router = APIRouter(prefix="/actions", tags=["actions"])


class ExecuteActionRequest(BaseModel):
    action_type: str = Field(..., description="Action type identifier (e.g. 'adjust_support_staffing')")
    approval_id: str = Field(..., description="Valid approved human authorization token")
    investigation_id: str = Field(..., description="ID of the originating investigation")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Execution parameters")


@router.post("/{action_id}/execute", summary="Execute Approved Operational Action (Safe Simulation)")
async def execute_action(
    action_id: str,
    req: ExecuteActionRequest,
    db: Session = Depends(get_db),
):
    """
    Execute a safe simulated operational action.
    Strictly verifies that approval_id is valid and in APPROVED state before executing.
    """
    # 1. Verify Approval State in Database
    approval = db.execute(
        select(ApprovalRequestModel).where(ApprovalRequestModel.approval_id == req.approval_id)
    ).scalar_one_or_none()

    if not approval:
        raise HTTPException(
            status_code=403,
            detail=f"Execution Rejected: Approval ID '{req.approval_id}' does not exist in approval registry.",
        )

    if approval.status != "APPROVED":
        raise HTTPException(
            status_code=403,
            detail=(
                f"Execution Rejected: Action requires APPROVED status, "
                f"but approval '{req.approval_id}' is currently '{approval.status}'."
            ),
        )

    # 2. Execute Action via LocalActionAgent
    action_agent = LocalActionAgent(db)
    action_input = ActionInput(
        action_id=action_id,
        action_type=ActionType(req.action_type),
        parameters=req.parameters,
        approval_id=req.approval_id,
        investigation_id=req.investigation_id,
    )

    output = await action_agent.execute(action_input)
    if output.status.value == "failed" or output.error:
        raise HTTPException(status_code=400, detail=output.error)

    # 3. Update Recommendation status to EXECUTED
    rec = db.execute(
        select(RecommendationModel).where(RecommendationModel.recommendation_id == approval.recommendation_id)
    ).scalar_one_or_none()
    if rec:
        rec.approval_status = "EXECUTED"
        db.commit()

    return output.model_dump()
