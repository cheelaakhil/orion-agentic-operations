"""
ORION MCP Tools — Recommendations and Human Governance

Safety Classification:
- get_recommendations: PROPOSAL
- request_approval: PROPOSAL
- approve_recommendation: APPROVAL
- reject_recommendation: APPROVAL
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from backend.core.database import SessionLocal
from backend.models.models import ApprovalRequestModel, RecommendationModel
from backend.services.audit import log_audit_event


def get_recommendations(investigation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve prioritized, evidence-backed action recommendations.

    Safety: PROPOSAL

    When to use:
    Call this to obtain ranked operational remediation recommendations proposed
    by the ORION RecommendationAgent.

    Inputs:
    - investigation_id: Optional investigation ID filter. If omitted, retrieves active proposals.

    Returns:
    List of recommendations with expected recovery impact, implementation effort,
    risk factors, and human approval status.
    """
    db = SessionLocal()
    try:
        query = select(RecommendationModel)
        if investigation_id:
            query = query.where(RecommendationModel.investigation_id == investigation_id)
        query = query.order_by(RecommendationModel.priority.asc())

        recs = db.scalars(query).all()
        if not recs:
            recs = db.scalars(select(RecommendationModel).order_by(RecommendationModel.priority.asc()).limit(4)).all()

        results = []
        for r in recs:
            results.append({
                "recommendation_id": r.recommendation_id,
                "investigation_id": r.investigation_id,
                "title": r.title,
                "description": r.description,
                "category": r.category,
                "priority": r.priority,
                "expected_impact": r.expected_impact,
                "action_type": r.action_type,
                "risks": r.risks,
                "requires_human_approval": r.requires_human_approval,
                "approval_status": r.approval_status,
            })

        return {
            "recommendations": results,
            "count": len(results),
        }
    finally:
        db.close()


def request_approval(recommendation_id: str) -> Dict[str, Any]:
    """
    Create a pending approval request for a proposed recommendation.

    Safety: PROPOSAL

    Note: This tool creates a PENDING authorization request for human executive review.
    It does NOT grant approval.

    Inputs:
    - recommendation_id: Unique recommendation ID (e.g. 'REC-001').

    Returns:
    Created approval request details with status 'PENDING_APPROVAL'.
    """
    db = SessionLocal()
    try:
        rec = db.scalar(select(RecommendationModel).where(RecommendationModel.recommendation_id == recommendation_id))
        if not rec:
            return {"error": f"Recommendation {recommendation_id} not found."}

        approval_id = f"APPR-{recommendation_id}"
        req = db.scalar(select(ApprovalRequestModel).where(ApprovalRequestModel.approval_id == approval_id))
        if not req:
            req = ApprovalRequestModel(
                approval_id=approval_id,
                recommendation_id=recommendation_id,
                investigation_id=rec.investigation_id,
                action_type=rec.action_type,
                status="PENDING_APPROVAL",
                requested_at=datetime.utcnow(),
            )
            db.add(req)
            db.commit()

            log_audit_event(
                db=db,
                event_type="APPROVAL_REQUESTED",
                entity_type="approval",
                entity_id=approval_id,
                action="request_approval",
                actor="mcp_governance_tool",
                status="PENDING_APPROVAL",
                details={"recommendation_id": recommendation_id, "action_type": rec.action_type},
            )

        return {
            "approval_id": approval_id,
            "recommendation_id": recommendation_id,
            "status": "PENDING_APPROVAL",
            "message": "Approval request created. Human executive review required before execution.",
        }
    finally:
        db.close()


def approve_recommendation(
    recommendation_id: str,
    approver: str = "ExecutiveOpsDirector",
    reason: str = "Approved via ORION MCP Governance Tool",
) -> Dict[str, Any]:
    """
    Formally grant executive human approval for a remediation proposal.

    Safety: APPROVAL

    When to use:
    Call this when a human decision-maker authorizes execution of a proposed operational action.
    This creates an authorized approval token enabling safe simulation execution.

    Inputs:
    - recommendation_id: Unique recommendation ID (e.g. 'REC-001').
    - approver: Authorized human operator or executive name.
    - reason: Explicit rationale for granting approval.

    Returns:
    Approval confirmation, generated approval_id token, and status 'APPROVED'.
    """
    db = SessionLocal()
    try:
        rec = db.scalar(select(RecommendationModel).where(RecommendationModel.recommendation_id == recommendation_id))
        if not rec:
            return {"error": f"Recommendation {recommendation_id} not found."}

        rec.approval_status = "APPROVED"
        approval_id = f"APPR-{recommendation_id}"
        req = db.scalar(select(ApprovalRequestModel).where(ApprovalRequestModel.approval_id == approval_id))
        if not req:
            req = ApprovalRequestModel(
                approval_id=approval_id,
                recommendation_id=recommendation_id,
                investigation_id=rec.investigation_id,
                action_type=rec.action_type,
                status="APPROVED",
                decided_by=approver,
                decision_reason=reason,
                requested_at=datetime.utcnow(),
                decided_at=datetime.utcnow(),
            )
            db.add(req)
        else:
            req.status = "APPROVED"
            req.decided_by = approver
            req.decision_reason = reason
            req.decided_at = datetime.utcnow()

        db.commit()

        log_audit_event(
            db=db,
            event_type="ACTION_APPROVED",
            entity_type="recommendation",
            entity_id=recommendation_id,
            action="approve_recommendation",
            actor=approver,
            status="APPROVED",
            details={"decision_reason": reason, "approval_id": approval_id},
        )

        return {
            "status": "APPROVED",
            "approval_id": approval_id,
            "recommendation_id": recommendation_id,
            "approver": approver,
            "decided_at": req.decided_at.isoformat(),
            "message": f"Recommendation {recommendation_id} approved. Safe simulation execution now authorized.",
        }
    finally:
        db.close()


def reject_recommendation(
    recommendation_id: str,
    approver: str = "ExecutiveOpsDirector",
    reason: str = "Rejected via ORION MCP Governance Tool",
) -> Dict[str, Any]:
    """
    Reject a proposed operational recommendation, permanently preventing execution.

    Safety: APPROVAL

    Inputs:
    - recommendation_id: Unique recommendation ID (e.g. 'REC-002').
    - approver: Authorized human operator name.
    - reason: Operational justification for rejection.

    Returns:
    Rejection confirmation with status 'REJECTED'.
    """
    db = SessionLocal()
    try:
        rec = db.scalar(select(RecommendationModel).where(RecommendationModel.recommendation_id == recommendation_id))
        if not rec:
            return {"error": f"Recommendation {recommendation_id} not found."}

        rec.approval_status = "REJECTED"
        approval_id = f"APPR-{recommendation_id}"
        req = db.scalar(select(ApprovalRequestModel).where(ApprovalRequestModel.approval_id == approval_id))
        if not req:
            req = ApprovalRequestModel(
                approval_id=approval_id,
                recommendation_id=recommendation_id,
                investigation_id=rec.investigation_id,
                action_type=rec.action_type,
                status="REJECTED",
                decided_by=approver,
                decision_reason=reason,
                requested_at=datetime.utcnow(),
                decided_at=datetime.utcnow(),
            )
            db.add(req)
        else:
            req.status = "REJECTED"
            req.decided_by = approver
            req.decision_reason = reason
            req.decided_at = datetime.utcnow()

        db.commit()

        log_audit_event(
            db=db,
            event_type="ACTION_REJECTED",
            entity_type="recommendation",
            entity_id=recommendation_id,
            action="reject_recommendation",
            actor=approver,
            status="REJECTED",
            details={"decision_reason": reason, "approval_id": approval_id},
        )

        return {
            "status": "REJECTED",
            "approval_id": approval_id,
            "recommendation_id": recommendation_id,
            "approver": approver,
            "decided_at": req.decided_at.isoformat(),
            "message": f"Recommendation {recommendation_id} rejected. Execution blocked.",
        }
    finally:
        db.close()
