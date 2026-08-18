"""
ORION Audit Trail REST API Endpoints.

Provides inspection endpoints for the immutable system audit log.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.models import AuditEvent

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", summary="Retrieve Audit Trail Logs")
def get_audit_trail_logs(
    event_type: str | None = Query(None, description="Filter by event type (e.g. 'ACTION_APPROVED')"),
    entity_id: str | None = Query(None, description="Filter by entity ID (e.g. 'ANOM-REV-001', 'REC-001')"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Retrieve immutable audit log events covering anomalies, investigation steps,
    approval state changes, and safe action execution records.
    """
    query = select(AuditEvent).order_by(desc(AuditEvent.timestamp))
    if event_type:
        query = query.where(AuditEvent.event_type == event_type)
    if entity_id:
        query = query.where(AuditEvent.entity_id == entity_id)

    query = query.offset(offset).limit(limit)
    events = db.execute(query).scalars().all()

    return [
        {
            "event_id": event.event_id or f"AUD-{event.id}",
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "action": event.action,
            "actor": event.actor,
            "status": event.status,
            "details": event.details,
        }
        for event in events
    ]
