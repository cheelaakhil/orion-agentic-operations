"""
Audit Service for ORION.

Provides immutable logging of all operational intelligence events,
investigation milestones, approval state transitions, and safe action executions.
"""

from datetime import datetime, timezone
from typing import Any
import uuid

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.models.models import AuditEvent


def log_audit_event(
    db: Session,
    event_type: str,
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str = "system",
    status: str = "SUCCESS",
    details: dict[str, Any] | None = None,
    event_id: str | None = None,
) -> AuditEvent:
    """
    Log an immutable audit event to the database.

    Event Types include:
    - ANOMALY_DETECTED
    - INVESTIGATION_STARTED
    - EVIDENCE_GENERATED
    - ROOT_CAUSE_IDENTIFIED
    - IMPACT_CALCULATED
    - RECOMMENDATION_CREATED
    - APPROVAL_REQUESTED
    - ACTION_APPROVED
    - ACTION_REJECTED
    - ACTION_EXECUTED
    """
    if not event_id:
        event_id = f"AUD-{uuid.uuid4().hex[:10].upper()}"

    now = datetime.now(timezone.utc)
    event = AuditEvent(
        event_id=event_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        status=status,
        details=details or {},
        timestamp=now,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_audit_trail(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    event_type: str | None = None,
    entity_id: str | None = None,
) -> list[AuditEvent]:
    """Retrieve audit events with optional filtering."""
    query = select(AuditEvent).order_by(desc(AuditEvent.timestamp))
    if event_type:
        query = query.where(AuditEvent.event_type == event_type)
    if entity_id:
        query = query.where(AuditEvent.entity_id == entity_id)

    query = query.offset(offset).limit(limit)
    return list(db.execute(query).scalars().all())


def get_audit_events_for_investigation(
    db: Session,
    investigation_id: str,
) -> list[AuditEvent]:
    """Retrieve all audit events related to an investigation workflow."""
    query = (
        select(AuditEvent)
        .where(
            (AuditEvent.entity_id == investigation_id)
            | (AuditEvent.details["investigation_id"].as_string() == investigation_id)
        )
        .order_by(AuditEvent.timestamp.asc())
    )
    return list(db.execute(query).scalars().all())
