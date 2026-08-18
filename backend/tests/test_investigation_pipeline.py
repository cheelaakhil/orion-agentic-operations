"""
Unit & Integration Tests for ORION Milestone 3: Complete Investigation Pipeline.

Tests:
1. LocalDataAnalysisAgent: Fact extraction & OBSERVED/INFERRED/HYPOTHESIS separation.
2. LocalAnomalyInvestigationAgent: Temporal propagation & finding extraction.
3. LocalRootCauseAgent: Hypothesis ranking & confidence derivation.
4. LocalBusinessImpactAgent: Deterministic loss & risk calculations.
5. LocalRecommendationAgent: Action ranking & feasibility analysis.
6. Approval Enforcement: Unapproved execution rejection & rejection workflow.
7. Safe Action Execution: Human-approved safe domain simulation.
8. Audit Trail Completeness: Logging of all milestone events.
9. Supervisor Orchestration E2E: Full pipeline coordination.
10. REST API Endpoints: Investigations, recommendations, approval, actions, audit.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from agents.implementations.local.action import LocalActionAgent
from agents.implementations.local.anomaly_investigation import LocalAnomalyInvestigationAgent
from agents.implementations.local.business_impact import LocalBusinessImpactAgent
from agents.implementations.local.data_analysis import LocalDataAnalysisAgent
from agents.implementations.local.recommendation import LocalRecommendationAgent
from agents.implementations.local.root_cause import LocalRootCauseAgent
from agents.interfaces.action import ActionInput, ActionType
from agents.interfaces.anomaly_investigation import AnomalyInvestigationInput
from agents.interfaces.base import AnomalyRecord, Severity, TimeRange
from agents.interfaces.business_impact import BusinessImpactInput
from agents.interfaces.data_analysis import DataAnalysisInput
from agents.interfaces.recommendation import RecommendationInput
from agents.interfaces.root_cause import RootCauseInput
from agents.interfaces.supervisor import InvestigationConfig, SupervisorInput
from agents.orchestrator.supervisor import SupervisorOrchestrator
from backend.core.database import get_db
from backend.main import app
from backend.models.models import ApprovalRequestModel, AuditEvent, RecommendationModel
from backend.services.audit import get_audit_trail, log_audit_event


@pytest.fixture
def standard_anomaly():
    return AnomalyRecord(
        anomaly_id="ANOM-REV-001",
        metric_name="daily_revenue",
        metric_value=163189.54,
        expected_value=286343.91,
        deviation_pct=-43.01,
        severity=Severity.CRITICAL,
        detected_at="2026-08-01T00:00:00",
    )


@pytest.mark.asyncio
async def test_data_analysis_agent(db_session: Session, standard_anomaly):
    """Test DataAnalysisAgent computes deterministic facts across dimensions."""
    agent = LocalDataAnalysisAgent(db_session)
    inp = DataAnalysisInput(
        investigation_id="TEST-INV-001",
        anomaly=standard_anomaly,
        dimensions=["revenue", "support", "inventory", "customers", "marketing"],
        time_range=TimeRange(start_date="2026-06-20", end_date="2026-08-01"),
    )
    output = await agent.execute(inp)
    assert output.investigation_id == "TEST-INV-001"
    assert "revenue" in output.dimension_analyses
    assert "support" in output.dimension_analyses
    assert "inventory" in output.dimension_analyses
    assert len(output.cross_dimension_correlations) >= 2
    assert output.data_quality.data_coverage_pct == 100.0


@pytest.mark.asyncio
async def test_anomaly_investigation_agent(db_session: Session, standard_anomaly):
    """Test AnomalyInvestigationAgent derives propagation paths and key findings."""
    da_agent = LocalDataAnalysisAgent(db_session)
    da_out = await da_agent.execute(
        DataAnalysisInput(
            investigation_id="TEST-INV-002",
            anomaly=standard_anomaly,
            dimensions=["revenue", "support", "inventory"],
            time_range=TimeRange(start_date="2026-06-20", end_date="2026-08-01"),
        )
    )

    inv_agent = LocalAnomalyInvestigationAgent()
    inv_out = await inv_agent.execute(
        AnomalyInvestigationInput(
            investigation_id="TEST-INV-002",
            anomaly=standard_anomaly,
            dimension_analyses=da_out.dimension_analyses,
            correlations=da_out.cross_dimension_correlations,
        )
    )
    assert len(inv_out.pattern_analysis.propagation_path) >= 2
    assert len(inv_out.key_findings) >= 2
    assert inv_out.anomaly_classification.onset_analysis.confidence > 0.8


@pytest.mark.asyncio
async def test_root_cause_agent(db_session: Session, standard_anomaly):
    """Test RootCauseAgent ranks hypotheses based on evidence strength."""
    da_agent = LocalDataAnalysisAgent(db_session)
    da_out = await da_agent.execute(
        DataAnalysisInput(
            investigation_id="TEST-INV-003",
            anomaly=standard_anomaly,
            dimensions=["revenue", "support", "inventory"],
            time_range=TimeRange(start_date="2026-06-20", end_date="2026-08-01"),
        )
    )
    inv_agent = LocalAnomalyInvestigationAgent()
    inv_out = await inv_agent.execute(
        AnomalyInvestigationInput(
            investigation_id="TEST-INV-003",
            anomaly=standard_anomaly,
            dimension_analyses=da_out.dimension_analyses,
            correlations=da_out.cross_dimension_correlations,
        )
    )

    rc_agent = LocalRootCauseAgent()
    rc_out = await rc_agent.execute(
        RootCauseInput(
            investigation_id="TEST-INV-003",
            anomaly=standard_anomaly,
            dimension_analyses=da_out.dimension_analyses,
            pattern_analysis=inv_out.pattern_analysis,
            anomaly_classification=inv_out.anomaly_classification,
        )
    )
    assert rc_out.primary_root_cause == "HYP-001"
    assert len(rc_out.hypotheses) >= 2
    assert rc_out.hypotheses[0].confidence >= 0.80
    assert len(rc_out.hypotheses[0].causal_chain) >= 2


@pytest.mark.asyncio
async def test_business_impact_agent(db_session: Session, standard_anomaly):
    """Test BusinessImpactAgent computes deterministic losses and forward risk."""
    bi_agent = LocalBusinessImpactAgent(db_session)
    bi_out = await bi_agent.execute(
        BusinessImpactInput(
            investigation_id="TEST-INV-004",
            anomaly=standard_anomaly,
            root_causes=[],
            dimension_analyses={},
        )
    )
    assert bi_out.realized_impact.revenue_loss > 0
    assert bi_out.projected_impact.revenue_at_risk_30d > 0
    assert bi_out.severity_assessment.level == Severity.CRITICAL


@pytest.mark.asyncio
async def test_recommendation_agent(db_session: Session, standard_anomaly):
    """Test RecommendationAgent produces prioritized, evidence-backed actions."""
    bi_agent = LocalBusinessImpactAgent(db_session)
    bi_out = await bi_agent.execute(
        BusinessImpactInput(
            investigation_id="TEST-INV-005",
            anomaly=standard_anomaly,
            root_causes=[],
            dimension_analyses={},
        )
    )

    rec_agent = LocalRecommendationAgent()
    rec_out = await rec_agent.execute(
        RecommendationInput(
            investigation_id="TEST-INV-005",
            root_causes=[],
            business_impact=bi_out,
        )
    )
    assert len(rec_out.recommendations) >= 3
    assert rec_out.recommendations[0].priority == 1
    assert rec_out.recommendations[0].category == "immediate"
    assert rec_out.recommendations[0].requires_approval is True


@pytest.mark.asyncio
async def test_approval_enforcement_and_rejection(db_session: Session):
    """Test that ActionAgent strictly rejects unapproved and rejected actions."""
    action_agent = LocalActionAgent(db_session)

    # 1. Non-existent approval must fail
    res_unauthorized = await action_agent.execute(
        ActionInput(
            action_id="ACT-TEST-001",
            action_type=ActionType.ADJUST_SUPPORT_STAFFING,
            parameters={},
            approval_id="APPR-FAKE-999",
            investigation_id="INV-TEST",
        )
    )
    assert res_unauthorized.status.value == "failed"
    assert "not found" in res_unauthorized.error.lower()

    # 2. PENDING_APPROVAL must fail
    appr_pending = ApprovalRequestModel(
        approval_id="APPR-TEST-PENDING",
        recommendation_id="REC-TEST-PENDING",
        investigation_id="INV-TEST",
        action_type="adjust_support_staffing",
        status="PENDING_APPROVAL",
    )
    db_session.add(appr_pending)
    db_session.commit()

    res_pending = await action_agent.execute(
        ActionInput(
            action_id="ACT-TEST-002",
            action_type=ActionType.ADJUST_SUPPORT_STAFFING,
            parameters={},
            approval_id="APPR-TEST-PENDING",
            investigation_id="INV-TEST",
        )
    )
    assert res_pending.status.value == "failed"
    assert "access denied" in res_pending.error.lower()

    # 3. REJECTED status must fail
    appr_pending.status = "REJECTED"
    db_session.commit()

    res_rejected = await action_agent.execute(
        ActionInput(
            action_id="ACT-TEST-003",
            action_type=ActionType.ADJUST_SUPPORT_STAFFING,
            parameters={},
            approval_id="APPR-TEST-PENDING",
            investigation_id="INV-TEST",
        )
    )
    assert res_rejected.status.value == "failed"


@pytest.mark.asyncio
async def test_approval_and_safe_action_execution(db_session: Session):
    """Test that ActionAgent executes safe simulation once APPROVED."""
    appr_approved = ApprovalRequestModel(
        approval_id="APPR-TEST-APPROVED",
        recommendation_id="REC-TEST-001",
        investigation_id="INV-TEST-001",
        action_type="adjust_support_staffing",
        status="APPROVED",
        decided_by="operations_lead",
    )
    db_session.add(appr_approved)
    db_session.commit()

    action_agent = LocalActionAgent(db_session)
    res = await action_agent.execute(
        ActionInput(
            action_id="ACT-TEST-APPROVED",
            action_type=ActionType.ADJUST_SUPPORT_STAFFING,
            parameters={"agents_to_add": 15},
            approval_id="APPR-TEST-APPROVED",
            investigation_id="INV-TEST-001",
        )
    )
    assert res.status.value == "success"
    assert res.result is not None
    assert len(res.result.changes_made) >= 2
    assert "support_sla_breach_rate" in res.result.metrics_affected


def test_audit_trail_lifecycle(db_session: Session):
    """Test logging and querying of all milestone audit events."""
    event_types = [
        "ANOMALY_DETECTED",
        "INVESTIGATION_STARTED",
        "EVIDENCE_GENERATED",
        "ROOT_CAUSE_IDENTIFIED",
        "IMPACT_CALCULATED",
        "RECOMMENDATION_CREATED",
        "APPROVAL_REQUESTED",
        "ACTION_APPROVED",
        "ACTION_REJECTED",
        "ACTION_EXECUTED",
    ]
    for et in event_types:
        log_audit_event(
            db=db_session,
            event_type=et,
            entity_type="test_entity",
            entity_id="ENT-001",
            action=f"action_{et.lower()}",
            actor="test_runner",
            status="SUCCESS",
            details={"type": et},
        )

    trail = get_audit_trail(db_session, limit=20, entity_id="ENT-001")
    logged_types = {e.event_type for e in trail}
    for et in event_types:
        assert et in logged_types


@pytest.mark.asyncio
async def test_supervisor_orchestration_e2e(db_session: Session, standard_anomaly):
    """Test full Supervisor end-to-end investigation pipeline."""
    supervisor = SupervisorOrchestrator(db_session)
    sup_input = SupervisorInput(
        anomaly=standard_anomaly,
        config=InvestigationConfig(
            time_range=TimeRange(start_date="2026-06-20", end_date="2026-08-01")
        ),
    )
    output = await supervisor.execute(sup_input)
    assert output.investigation_id.startswith("INV-")
    assert len(output.timeline) == 5
    assert len(output.root_causes) >= 2
    assert output.confidence_score >= 0.8
    assert output.business_impact.total_revenue_loss > 0
    assert len(output.recommendations) >= 3
    assert output.requires_approval is True


def test_investigation_rest_api_lifecycle(db_session: Session):
    """Test full REST API lifecycle: create investigation -> get -> approve -> execute -> audit."""
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    # 1. Trigger Investigation
    res_inv = client.post(
        "/api/v1/investigations",
        json={"anomaly_id": "ANOM-REV-001"},
    )
    assert res_inv.status_code == 200
    inv_data = res_inv.json()
    investigation_id = inv_data["investigation_id"]
    assert investigation_id.startswith("INV-")

    # 2. Get Investigation Details
    res_get_inv = client.get(f"/api/v1/investigations/{investigation_id}")
    assert res_get_inv.status_code == 200
    assert res_get_inv.json()["investigation_id"] == investigation_id

    # 3. Get Recommendations
    res_recs = client.get(f"/api/v1/investigations/{investigation_id}/recommendations")
    assert res_recs.status_code == 200
    recs = res_recs.json()
    assert len(recs) >= 3
    first_rec = recs[0]
    rec_id = first_rec["recommendation_id"]

    # 4. Attempt to execute without approval (Must return 403)
    res_exec_unapproved = client.post(
        "/api/v1/actions/ACT-UNAUTH/execute",
        json={
            "action_type": first_rec["action_type"],
            "approval_id": f"APPR-{rec_id}",
            "investigation_id": investigation_id,
        },
    )
    assert res_exec_unapproved.status_code == 403

    # 5. Approve the recommendation
    res_approve = client.post(
        f"/api/v1/recommendations/{rec_id}/approve",
        json={"decision_reason": "Authorized by Operations Director", "decided_by": "OpsLead"},
    )
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "APPROVED"
    approval_id = res_approve.json()["approval_id"]

    # 6. Execute approved action
    res_exec = client.post(
        f"/api/v1/actions/ACT-{rec_id}/execute",
        json={
            "action_type": first_rec["action_type"],
            "approval_id": approval_id,
            "investigation_id": investigation_id,
        },
    )
    assert res_exec.status_code == 200
    assert res_exec.json()["status"] == "success"

    # 7. Test rejection workflow on second recommendation
    second_rec = recs[1]
    second_rec_id = second_rec["recommendation_id"]
    res_reject = client.post(
        f"/api/v1/recommendations/{second_rec_id}/reject",
        json={"decision_reason": "Budget constrained this sprint", "decided_by": "FinanceLead"},
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "REJECTED"

    # Execution of rejected recommendation must fail
    res_exec_rejected = client.post(
        f"/api/v1/actions/ACT-{second_rec_id}/execute",
        json={
            "action_type": second_rec["action_type"],
            "approval_id": f"APPR-{second_rec_id}",
            "investigation_id": investigation_id,
        },
    )
    assert res_exec_rejected.status_code == 403

    # 8. Query Audit Trail
    res_audit = client.get("/api/v1/audit")
    assert res_audit.status_code == 200
    audit_events = res_audit.json()
    assert len(audit_events) > 0

    app.dependency_overrides.clear()
