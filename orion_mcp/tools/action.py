"""
ORION MCP Tools — Controlled Action Simulation

Safety Classification: CONSEQUENTIAL_ACTION
Executes domain-specific operational action simulations ONLY when authorized by a valid, approved token.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import select
from agents.implementations.local.action import LocalActionAgent
from agents.interfaces.action import ActionInput, ActionType
from backend.core.database import SessionLocal
from backend.models.models import ActionExecutionModel, ApprovalRequestModel, RecommendationModel
from backend.services.audit import log_audit_event


def execute_approved_action(
    action_id: str,
    approval_id: str,
    investigation_id: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute an approved operational remediation action in safe simulation mode.

    Safety: CONSEQUENTIAL_ACTION

    CRITICAL GOVERNANCE RULES:
    Execution MUST fail if:
    1. approval_id is missing or invalid.
    2. approval record does not exist in the database.
    3. approval status is NOT 'APPROVED' (e.g. 'PENDING_APPROVAL' or 'REJECTED').
    4. recommendation was previously rejected.
    5. action was already executed.

    Inputs:
    - action_id: Action identifier (e.g. 'ACT-REC-001').
    - approval_id: Valid authorization token (e.g. 'APPR-REC-001').
    - investigation_id: Associated investigation ID.
    - parameters: Optional execution parameter overrides (e.g. {'agents_to_add': 15}).

    Returns:
    JSON execution result containing execution_id, status ('success'), simulation details,
    simulated changes made, affected metrics, and confirmation that changes are labeled SIMULATED.
    """
    if not approval_id:
        return {
            "status": "error",
            "error": "EXECUTION_DENIED: approval_id is required. No consequential action may execute without human authorization.",
        }

    db = SessionLocal()
    try:
        # 1. Verify approval record
        approval = db.scalar(
            select(ApprovalRequestModel).where(ApprovalRequestModel.approval_id == approval_id)
        )
        if not approval:
            return {
                "status": "error",
                "error": f"EXECUTION_DENIED: Approval token '{approval_id}' does not exist.",
            }

        if approval.status != "APPROVED":
            return {
                "status": "error",
                "error": f"EXECUTION_DENIED: Action is not approved. Current approval status: '{approval.status}'.",
            }

        # 2. Check recommendation status
        if approval.recommendation_id:
            rec = db.scalar(
                select(RecommendationModel).where(RecommendationModel.recommendation_id == approval.recommendation_id)
            )
            if rec and rec.approval_status == "REJECTED":
                return {
                    "status": "error",
                    "error": "EXECUTION_DENIED: Associated recommendation was explicitly REJECTED by human operator.",
                }

        # 3. Check for duplicate execution after approval decision
        if approval.decided_at:
            existing_exec = db.scalar(
                select(ActionExecutionModel).where(
                    ActionExecutionModel.approval_id == approval_id,
                    ActionExecutionModel.status == "SUCCESS",
                    ActionExecutionModel.executed_at >= approval.decided_at,
                )
            )
            if existing_exec:
                return {
                    "status": "error",
                    "error": f"EXECUTION_DENIED: Action for approval '{approval_id}' was already executed (Execution ID: {existing_exec.execution_id}).",
                }

        # 4. Map action type
        raw_type = approval.action_type or "adjust_support_staffing"
        try:
            act_type = ActionType(raw_type)
        except ValueError:
            act_type = ActionType.ADJUST_SUPPORT_STAFFING

        # 5. Execute via LocalActionAgent
        agent = LocalActionAgent(db)
        inv_id = investigation_id or approval.investigation_id or "INV-UNKNOWN"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(
            agent.execute(
                ActionInput(
                    action_id=action_id,
                    investigation_id=inv_id,
                    recommendation_id=approval.recommendation_id or "REC-001",
                    action_type=act_type,
                    parameters=parameters or {},
                    approval_id=approval_id,
                    simulated=True,
                )
            )
        )
        loop.close()

        res_dict = output.result.model_dump() if hasattr(output.result, "model_dump") else output.result

        # Update approval status to EXECUTED
        approval.status = "EXECUTED"

        if approval.recommendation_id:
            rec = db.scalar(select(RecommendationModel).where(RecommendationModel.recommendation_id == approval.recommendation_id))
            if rec:
                rec.approval_status = "EXECUTED"

        db.commit()

        return {
            "status": "success",
            "execution_id": output.execution_id,
            "action_id": action_id,
            "action_type": act_type.value,
            "approval_id": approval_id,
            "execution_mode": "SIMULATED ACTION",
            "result": res_dict,
            "executed_at": datetime.utcnow().isoformat(),
            "message": "Safe simulation completed successfully and logged to immutable audit trail.",
        }
    finally:
        db.close()
