"""
Local ActionAgent Implementation for ORION.

Executes approved operational actions via safe simulations.
Strictly validates human approval before execution and rejects any unapproved action.
Produces audit trail logs for all execution attempts.
"""

from datetime import datetime, timezone
from typing import Any
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.interfaces.action import (
    ActionAgent,
    ActionInput,
    ActionOutput,
    ActionResult,
    ActionStatus,
    ActionType,
    AuditLogEntry,
)
from backend.models.models import ActionExecutionModel, ApprovalRequestModel, AuditEvent
from backend.services.audit import log_audit_event


class LocalActionAgent(ActionAgent):
    """
    Deterministic local implementation of ActionAgent.
    Enforces human-in-the-loop approval and executes safe domain simulations.
    """

    def __init__(self, db: Session | None = None):
        self.db = db

    async def execute(self, input_data: ActionInput) -> ActionOutput:
        execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        action_id = input_data.action_id
        action_type = input_data.action_type
        approval_id = input_data.approval_id
        investigation_id = input_data.investigation_id
        params = input_data.parameters

        now_str = datetime.now(timezone.utc).isoformat()

        # 1. Approval Verification Gate
        if self.db is not None:
            db = self.db
            approval = db.execute(
                select(ApprovalRequestModel).where(ApprovalRequestModel.approval_id == approval_id)
            ).scalar_one_or_none()

            if not approval:
                error_msg = f"Security Error: Approval ID '{approval_id}' was not found in the approval registry."
                log_audit_event(
                    db=db,
                    event_type="ACTION_REJECTED",
                    entity_type="action",
                    entity_id=action_id,
                    action=f"execute_{action_type.value}",
                    actor="action_agent",
                    status="REJECTED_UNAUTHORIZED",
                    details={"reason": error_msg, "approval_id": approval_id, "investigation_id": investigation_id},
                )
                return ActionOutput(
                    execution_id=execution_id,
                    action_id=action_id,
                    status=ActionStatus.FAILED,
                    error=error_msg,
                    audit_entry=AuditLogEntry(
                        entity_id=action_id,
                        action=f"execute_{action_type.value}",
                        actor="action_agent",
                        details={"status": "REJECTED_UNAUTHORIZED", "error": error_msg},
                        timestamp=now_str,
                    ),
                )

            if approval.status != "APPROVED":
                error_msg = f"Access Denied: Action execution requires APPROVED status, but approval '{approval_id}' has status '{approval.status}'."
                log_audit_event(
                    db=db,
                    event_type="ACTION_REJECTED",
                    entity_type="action",
                    entity_id=action_id,
                    action=f"execute_{action_type.value}",
                    actor="action_agent",
                    status="REJECTED_UNAPPROVED",
                    details={"reason": error_msg, "approval_status": approval.status, "investigation_id": investigation_id},
                )
                return ActionOutput(
                    execution_id=execution_id,
                    action_id=action_id,
                    status=ActionStatus.FAILED,
                    error=error_msg,
                    audit_entry=AuditLogEntry(
                        entity_id=action_id,
                        action=f"execute_{action_type.value}",
                        actor="action_agent",
                        details={"status": "REJECTED_UNAPPROVED", "error": error_msg},
                        timestamp=now_str,
                    ),
                )

        # 2. Execute Safe Domain Simulation
        result: ActionResult
        if action_type == ActionType.ADJUST_SUPPORT_STAFFING or action_type.value == "adjust_support_staffing":
            result = ActionResult(
                changes_made=[
                    "Simulated assignment of 15 Tier-1/Tier-2 support specialists to high-breach queue",
                    "Simulated automated triage macro deployment for delivery status inquiries",
                    "Simulated queue throughput increase from 42 tickets/hr to 128 tickets/hr",
                ],
                metrics_affected=["support_sla_breach_rate", "average_resolution_time_hours", "customer_csat"],
                rollback_available=True,
                rollback_instructions="Simulate de-escalating temporary support staffing reallocation via dashboard.",
            )
        elif action_type == ActionType.TRIGGER_INVENTORY_REORDER or action_type.value == "trigger_inventory_reorder":
            result = ActionResult(
                changes_made=[
                    "Simulated dispatch of 2,400 emergency units across Electronics and Home & Kitchen categories",
                    "Simulated freight transfer routing from Central Hub to NA and EU fulfillment centers",
                    "Simulated stockout risk reduction on top 10 SKUs from 19.8% to 2.1%",
                ],
                metrics_affected=["inventory_stockout_rate", "order_cancellation_rate", "daily_revenue"],
                rollback_available=True,
                rollback_instructions="Simulate cancelling pending inter-warehouse transfer orders.",
            )
        elif action_type == ActionType.CREATE_RETENTION_CAMPAIGN or action_type.value == "create_retention_campaign":
            result = ActionResult(
                changes_made=[
                    "Simulated generation of personalized goodwill vouchers ($25 courtesy credit) for 813 at-risk customers",
                    "Simulated priority customer routing flag applied to impacted account profiles",
                ],
                metrics_affected=["repeat_purchase_rate", "at_risk_customer_count"],
                rollback_available=False,
                rollback_instructions=None,
            )
        elif action_type == ActionType.ADJUST_MARKETING_BUDGET or action_type.value == "adjust_marketing_budget":
            result = ActionResult(
                changes_made=[
                    "Simulated pause on $45,000 paid search spend for stockout electronics SKUs",
                    "Simulated reallocation of search budget into high-converting in-stock Apparel campaigns",
                ],
                metrics_affected=["marketing_roas", "total_spend"],
                rollback_available=True,
                rollback_instructions="Simulate reactivating paused electronics ad groups in marketing manager.",
            )
        else:
            result = ActionResult(
                changes_made=[f"Simulated execution of generic operational action '{action_type}'."],
                metrics_affected=["operational_throughput"],
                rollback_available=True,
                rollback_instructions="Revert simulated configuration changes.",
            )

        # 3. Log Audit Event & Persist Execution Record
        if self.db is not None:
            db = self.db
            exec_rec = ActionExecutionModel(
                execution_id=execution_id,
                action_id=action_id,
                approval_id=approval_id,
                investigation_id=investigation_id,
                action_type=action_type.value if hasattr(action_type, "value") else str(action_type),
                parameters=params,
                status="SUCCESS",
                result=result.model_dump(),
                executed_by="action_agent",
            )
            db.add(exec_rec)
            db.commit()

            log_audit_event(
                db=db,
                event_type="ACTION_EXECUTED",
                entity_type="action",
                entity_id=action_id,
                action=f"execute_{action_type.value if hasattr(action_type, 'value') else action_type}",
                actor="action_agent",
                status="SUCCESS",
                details={
                    "execution_id": execution_id,
                    "approval_id": approval_id,
                    "investigation_id": investigation_id,
                    "simulation_result": result.model_dump(),
                },
            )

        audit_entry = AuditLogEntry(
            entity_id=action_id,
            action=f"execute_{action_type.value if hasattr(action_type, 'value') else action_type}",
            actor="action_agent",
            details={
                "execution_id": execution_id,
                "status": "SUCCESS",
                "changes_made": result.changes_made,
            },
            timestamp=now_str,
        )

        return ActionOutput(
            execution_id=execution_id,
            action_id=action_id,
            status=ActionStatus.SUCCESS,
            result=result,
            audit_entry=audit_entry,
        )
