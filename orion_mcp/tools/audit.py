"""
ORION MCP Tools — Immutable Operations Audit Log

Safety Classification: READ_ONLY
Retrieves chronological audit events tracking AI actions, human approvals, and operational changes.
"""

from typing import Any, Dict, List, Optional
from backend.core.database import SessionLocal
from backend.services.audit import get_audit_trail as fetch_audit_events


def get_audit_events(
    entity_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Retrieve chronological audit trail entries from ORION's immutable operational event log.

    Safety: READ_ONLY

    When to use:
    Call this to verify audit history, inspect human authorization decisions,
    or trace agent investigation lifecycle milestones.

    Inputs:
    - entity_id: Optional filter for specific anomaly, investigation, recommendation, or action ID.
    - event_type: Optional filter (e.g. 'ANOMALY_DETECTED', 'INVESTIGATION_STARTED', 'ACTION_APPROVED', 'ACTION_EXECUTED').
    - limit: Maximum number of records to retrieve (default 50).

    Returns:
    List of audit event objects with timestamps, actors, actions, statuses, and payload metadata.
    """
    db = SessionLocal()
    try:
        events = fetch_audit_events(
            db=db,
            entity_id=entity_id,
            event_type=event_type,
            limit=limit,
        )

        return {
            "audit_events": [
                {
                    "event_id": ev.event_id,
                    "event_type": ev.event_type,
                    "entity_type": ev.entity_type,
                    "entity_id": ev.entity_id,
                    "action": ev.action,
                    "actor": ev.actor,
                    "status": ev.status,
                    "details": ev.details,
                    "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                }
                for ev in events
            ],
            "total_retrieved": len(events),
        }
    finally:
        db.close()
