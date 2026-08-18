"""
ORION Investigations REST API Endpoints.

Provides endpoints to initiate and inspect autonomous investigation workflows.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from agents.interfaces.base import AnomalyRecord, Severity, TimeRange
from agents.interfaces.supervisor import InvestigationConfig, SupervisorInput
from agents.orchestrator.supervisor import SupervisorOrchestrator
from backend.core.database import get_db
from backend.models.models import (
    AnomalyRecordModel,
    ApprovalRequestModel,
    InvestigationModel,
    RecommendationModel,
)

router = APIRouter(prefix="/investigations", tags=["investigations"])


class CreateInvestigationRequest(BaseModel):
    anomaly_id: str = Field(..., description="ID of the detected anomaly (e.g. 'ANOM-REV-001')")
    time_range: TimeRange | None = Field(default=None, description="Optional custom time range")
    dimensions: list[str] | None = Field(default=None, description="Optional subset of dimensions")


@router.post("", summary="Initiate Anomaly Investigation Pipeline")
async def create_investigation(
    req: CreateInvestigationRequest,
    db: Session = Depends(get_db),
):
    """
    Launch the full multi-agent investigation pipeline for an anomaly.
    Coordinates DataAnalysis, AnomalyInvestigation, RootCause, BusinessImpact,
    and Recommendation agents.
    """
    # 1. Look up anomaly record in DB or construct standard reference
    anomaly_model = db.execute(
        select(AnomalyRecordModel).where(AnomalyRecordModel.anomaly_id == req.anomaly_id)
    ).scalar_one_or_none()

    if anomaly_model:
        anomaly_rec = AnomalyRecord(
            anomaly_id=anomaly_model.anomaly_id,
            metric_name=anomaly_model.metric_name,
            metric_value=anomaly_model.metric_value,
            expected_value=anomaly_model.baseline_value,
            deviation_pct=anomaly_model.deviation_pct,
            severity=Severity(anomaly_model.severity.lower()),
            detected_at=anomaly_model.detected_at.isoformat(),
        )
    else:
        # Standard anomaly reference for ANOM-REV-001 / fallback
        anomaly_rec = AnomalyRecord(
            anomaly_id=req.anomaly_id,
            metric_name="daily_revenue",
            metric_value=163189.54,
            expected_value=286343.91,
            deviation_pct=-43.01,
            severity=Severity.CRITICAL,
            detected_at="2026-08-01T00:00:00",
        )

    # 2. Run Supervisor Pipeline
    config = InvestigationConfig()
    if req.time_range:
        config.time_range = req.time_range
    if req.dimensions:
        config.dimensions = req.dimensions

    supervisor = SupervisorOrchestrator(db)
    supervisor_input = SupervisorInput(anomaly=anomaly_rec, config=config)

    output = await supervisor.execute(supervisor_input)
    return output.model_dump()


@router.get("", summary="List All Investigations")
def list_investigations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieve all past and active investigations."""
    query = (
        select(InvestigationModel)
        .order_by(desc(InvestigationModel.started_at))
        .offset(offset)
        .limit(limit)
    )
    records = db.execute(query).scalars().all()
    return [
        {
            "investigation_id": rec.investigation_id,
            "anomaly_id": rec.anomaly_id,
            "status": rec.status,
            "confidence_score": rec.confidence_score,
            "summary": rec.summary,
            "started_at": rec.started_at.isoformat(),
            "completed_at": rec.completed_at.isoformat() if rec.completed_at else None,
            "requires_approval": rec.requires_approval,
        }
        for rec in records
    ]


@router.get("/{investigation_id}", summary="Get Detailed Investigation Dossier")
def get_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve full investigation details including timeline, root cause, and business impact."""
    record = db.execute(
        select(InvestigationModel).where(InvestigationModel.investigation_id == investigation_id)
    ).scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail=f"Investigation '{investigation_id}' not found")

    return {
        "investigation_id": record.investigation_id,
        "anomaly_id": record.anomaly_id,
        "status": record.status,
        "confidence_score": record.confidence_score,
        "summary": record.summary,
        "root_causes": record.root_causes,
        "business_impact": record.business_impact,
        "timeline": record.timeline,
        "observations": record.observations,
        "requires_approval": record.requires_approval,
        "started_at": record.started_at.isoformat(),
        "completed_at": record.completed_at.isoformat() if record.completed_at else None,
    }


@router.get("/{investigation_id}/recommendations", summary="Get Recommendations for Investigation")
def get_investigation_recommendations(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve all ranked recommendations formulated for an investigation."""
    query = (
        select(RecommendationModel)
        .where(RecommendationModel.investigation_id == investigation_id)
        .order_by(RecommendationModel.priority.asc())
    )
    records = db.execute(query).scalars().all()

    return [
        {
            "recommendation_id": rec.recommendation_id,
            "investigation_id": rec.investigation_id,
            "title": rec.title,
            "description": rec.description,
            "category": rec.category,
            "priority": rec.priority,
            "expected_impact": rec.expected_impact,
            "implementation": rec.implementation,
            "risks": rec.risks,
            "addresses_root_cause": rec.addresses_root_cause,
            "requires_human_approval": rec.requires_human_approval,
            "action_type": rec.action_type,
            "approval_status": rec.approval_status,
            "created_at": rec.created_at.isoformat(),
        }
        for rec in records
    ]
