"""
ORION Anomalies API Router

REST endpoints for triggering anomaly detection and retrieving quantitative evidence packages.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.analytics.anomalies import (
    AnomalyResult,
    DeterministicAnomalyEngine,
    anomaly_engine,
)
from backend.services.analytics.evidence import (
    EvidencePackage,
    generate_evidence_package,
)

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


def parse_date(d_str: str | None, default: datetime) -> datetime:
    if not d_str:
        return default
    return datetime.fromisoformat(d_str)


@router.get("", response_model=list[AnomalyResult])
def list_detected_anomalies(
    baseline_start: str | None = Query(None, description="YYYY-MM-DD"),
    baseline_end: str | None = Query(None, description="YYYY-MM-DD"),
    eval_start: str | None = Query(None, description="YYYY-MM-DD"),
    eval_end: str | None = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
) -> list[AnomalyResult]:
    """
    Run deterministic anomaly detection comparing baseline vs evaluation periods.
    Default baseline: 2026-05-01 to 2026-06-19.
    Default evaluation: 2026-06-20 to 2026-08-01.
    """
    b_start = parse_date(baseline_start, datetime(2026, 5, 1))
    b_end = parse_date(baseline_end, datetime(2026, 6, 19, 23, 59, 59))
    e_start = parse_date(eval_start, datetime(2026, 6, 20))
    e_end = parse_date(eval_end, datetime(2026, 8, 1, 23, 59, 59))

    anomalies = anomaly_engine.detect_all_anomalies(
        db=db,
        baseline_start=b_start,
        baseline_end=b_end,
        evaluation_start=e_start,
        evaluation_end=e_end,
    )
    return anomalies


@router.get("/{anomaly_id}/evidence", response_model=EvidencePackage)
def get_anomaly_evidence_package(
    anomaly_id: str,
    baseline_start: str | None = Query(None),
    baseline_end: str | None = Query(None),
    eval_start: str | None = Query(None),
    eval_end: str | None = Query(None),
    db: Session = Depends(get_db),
) -> EvidencePackage:
    """
    Retrieve comprehensive quantitative evidence package across all business dimensions
    for a specific detected anomaly.
    """
    b_start = parse_date(baseline_start, datetime(2026, 5, 1))
    b_end = parse_date(baseline_end, datetime(2026, 6, 19, 23, 59, 59))
    e_start = parse_date(eval_start, datetime(2026, 6, 20))
    e_end = parse_date(eval_end, datetime(2026, 8, 1, 23, 59, 59))

    # Find matching anomaly
    anomalies = anomaly_engine.detect_all_anomalies(
        db=db,
        baseline_start=b_start,
        baseline_end=b_end,
        evaluation_start=e_start,
        evaluation_end=e_end,
    )

    matched_anomaly = next((a for a in anomalies if a.anomaly_id == anomaly_id), None)
    if not matched_anomaly:
        # If not among defaults, construct placeholder target
        matched_anomaly = AnomalyResult(
            anomaly_id=anomaly_id,
            metric="daily_revenue",
            current_value=0.0,
            baseline_value=0.0,
            change_absolute=0.0,
            change_percentage=0.0,
            severity="MEDIUM",
            affected_dimension="revenue",
        )

    evidence_pkg = generate_evidence_package(
        db=db,
        anomaly=matched_anomaly,
        baseline_start=b_start,
        baseline_end=b_end,
        evaluation_start=e_start,
        evaluation_end=e_end,
    )
    return evidence_pkg
