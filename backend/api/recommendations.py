"""
ORION Recommendations & Human Approval REST API Endpoints.

Handles human-in-the-loop review, approval, and rejection of action proposals.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.models import ApprovalRequestModel, RecommendationModel
from backend.services.audit import log_audit_event

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class ApprovalDecisionRequest(BaseModel):
    decision_reason: str = Field(default="Approved by operations manager", description="Justification for the decision")
    decided_by: str = Field(default="human_operator", description="Identifier of the human approver")


@router.post("/{recommendation_id}/approve", summary="Approve Recommendation & Authorize Action")
def approve_recommendation(
    recommendation_id: str,
    req: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
):
    """
    Explicitly approve a proposed action recommendation.
    Transitions status from PENDING_APPROVAL -> APPROVED and logs to immutable audit trail.
    """
    rec = db.execute(
        select(RecommendationModel).where(RecommendationModel.recommendation_id == recommendation_id)
    ).scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail=f"Recommendation '{recommendation_id}' not found")

    approval = db.execute(
        select(ApprovalRequestModel).where(ApprovalRequestModel.recommendation_id == recommendation_id)
    ).scalar_one_or_none()

    now = datetime.now(timezone.utc)

    # Update Recommendation Model
    rec.approval_status = "APPROVED"

    # Update or Create Approval Request Model
    if approval:
        approval.status = "APPROVED"
        approval.decision_reason = req.decision_reason
        approval.decided_by = req.decided_by
        approval.decided_at = now
        approval_id = approval.approval_id
    else:
        approval_id = f"APPR-{recommendation_id}"
        approval = ApprovalRequestModel(
            approval_id=approval_id,
            recommendation_id=recommendation_id,
            investigation_id=rec.investigation_id,
            action_type=rec.action_type,
            action_details=rec.action_parameters or {},
            status="APPROVED",
            decision_reason=req.decision_reason,
            decided_by=req.decided_by,
            requested_at=now,
            decided_at=now,
        )
        db.add(approval)

    db.commit()

    # Log Audit Event
    log_audit_event(
        db=db,
        event_type="ACTION_APPROVED",
        entity_type="recommendation",
        entity_id=recommendation_id,
        action="approve_recommendation",
        actor=req.decided_by,
        status="APPROVED",
        details={
            "approval_id": approval_id,
            "investigation_id": rec.investigation_id,
            "action_type": rec.action_type,
            "reason": req.decision_reason,
        },
    )

    return {
        "status": "APPROVED",
        "recommendation_id": recommendation_id,
        "approval_id": approval_id,
        "action_type": rec.action_type,
        "authorized_by": req.decided_by,
        "decided_at": now.isoformat(),
        "message": f"Recommendation '{recommendation_id}' successfully approved. Action is authorized for execution.",
    }


@router.post("/{recommendation_id}/reject", summary="Reject Recommendation")
def reject_recommendation(
    recommendation_id: str,
    req: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
):
    """
    Explicitly reject a proposed action recommendation.
    Transitions status from PENDING_APPROVAL -> REJECTED and blocks any execution.
    """
    rec = db.execute(
        select(RecommendationModel).where(RecommendationModel.recommendation_id == recommendation_id)
    ).scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail=f"Recommendation '{recommendation_id}' not found")

    approval = db.execute(
        select(ApprovalRequestModel).where(ApprovalRequestModel.recommendation_id == recommendation_id)
    ).scalar_one_or_none()

    now = datetime.now(timezone.utc)

    # Update Recommendation Model
    rec.approval_status = "REJECTED"

    # Update or Create Approval Request Model
    if approval:
        approval.status = "REJECTED"
        approval.decision_reason = req.decision_reason
        approval.decided_by = req.decided_by
        approval.decided_at = now
        approval_id = approval.approval_id
    else:
        approval_id = f"APPR-{recommendation_id}"
        approval = ApprovalRequestModel(
            approval_id=approval_id,
            recommendation_id=recommendation_id,
            investigation_id=rec.investigation_id,
            action_type=rec.action_type,
            action_details=rec.action_parameters or {},
            status="REJECTED",
            decision_reason=req.decision_reason,
            decided_by=req.decided_by,
            requested_at=now,
            decided_at=now,
        )
        db.add(approval)

    db.commit()

    # Log Audit Event
    log_audit_event(
        db=db,
        event_type="ACTION_REJECTED",
        entity_type="recommendation",
        entity_id=recommendation_id,
        action="reject_recommendation",
        actor=req.decided_by,
        status="REJECTED",
        details={
            "approval_id": approval_id,
            "investigation_id": rec.investigation_id,
            "action_type": rec.action_type,
            "reason": req.decision_reason,
        },
    )

    return {
        "status": "REJECTED",
        "recommendation_id": recommendation_id,
        "approval_id": approval_id,
        "action_type": rec.action_type,
        "decided_by": req.decided_by,
        "decided_at": now.isoformat(),
        "message": f"Recommendation '{recommendation_id}' has been rejected. Action execution is blocked.",
    }
