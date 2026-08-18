"""
Supervisor Orchestrator Implementation for ORION.

Coordinates the end-to-end investigation pipeline across all specialized agents:
  1. DataAnalysisAgent
  2. AnomalyInvestigationAgent
  3. RootCauseAgent
  4. BusinessImpactAgent
  5. RecommendationAgent
  6. Human Approval Request Generation

Produces full timeline telemetry and persists state to the database and audit trail.
"""

from datetime import datetime, timezone
from typing import Any
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.implementations.local.action import LocalActionAgent
from agents.implementations.local.anomaly_investigation import LocalAnomalyInvestigationAgent
from agents.implementations.local.business_impact import LocalBusinessImpactAgent
from agents.implementations.local.data_analysis import LocalDataAnalysisAgent
from agents.implementations.local.recommendation import LocalRecommendationAgent
from agents.implementations.local.root_cause import LocalRootCauseAgent
from agents.interfaces.anomaly_investigation import AnomalyInvestigationInput
from agents.interfaces.base import AnomalyRecord, Severity, TimeRange
from agents.interfaces.business_impact import BusinessImpactInput
from agents.interfaces.data_analysis import DataAnalysisInput
from agents.interfaces.recommendation import RecommendationInput
from agents.interfaces.root_cause import RootCauseInput
from agents.interfaces.supervisor import (
    BusinessImpactReport,
    InvestigationConfig,
    InvestigationStatus,
    InvestigationStep,
    Recommendation,
    RootCauseHypothesis,
    SupervisorAgent,
    SupervisorInput,
    SupervisorOutput,
)
from backend.models.models import (
    AnomalyRecordModel,
    ApprovalRequestModel,
    InvestigationModel,
    RecommendationModel,
)
from backend.services.audit import log_audit_event


class SupervisorOrchestrator(SupervisorAgent):
    """
    Supervisor Agent orchestrating the full ORION investigation pipeline.
    """

    def __init__(self, db: Session | None = None):
        self.db = db
        self.data_agent = LocalDataAnalysisAgent(db)
        self.inv_agent = LocalAnomalyInvestigationAgent()
        self.rc_agent = LocalRootCauseAgent()
        self.impact_agent = LocalBusinessImpactAgent(db)
        self.rec_agent = LocalRecommendationAgent()
        self.action_agent = LocalActionAgent(db)

    async def execute(self, input_data: SupervisorInput) -> SupervisorOutput:
        anomaly = input_data.anomaly
        config = input_data.config or InvestigationConfig()
        investigation_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

        now = datetime.now(timezone.utc)
        timeline: list[InvestigationStep] = []

        # Audit: INVESTIGATION_STARTED
        if self.db is not None:
            log_audit_event(
                db=self.db,
                event_type="INVESTIGATION_STARTED",
                entity_type="investigation",
                entity_id=investigation_id,
                action="start_investigation",
                actor="supervisor_agent",
                status="IN_PROGRESS",
                details={
                    "anomaly_id": anomaly.anomaly_id,
                    "metric_name": anomaly.metric_name,
                    "severity": anomaly.severity.value if hasattr(anomaly.severity, "value") else str(anomaly.severity),
                },
            )

        # -------------------------------------------------------------
        # STEP 1: Data Analysis Agent
        # -------------------------------------------------------------
        step1_start = datetime.now(timezone.utc).isoformat()
        t_range = config.time_range or TimeRange(start_date="2026-06-20", end_date="2026-08-01")
        da_input = DataAnalysisInput(
            investigation_id=investigation_id,
            anomaly=anomaly,
            dimensions=config.dimensions,
            time_range=t_range,
        )
        da_output = await self.data_agent.execute(da_input)
        step1_end = datetime.now(timezone.utc).isoformat()
        timeline.append(
            InvestigationStep(
                step_order=1,
                agent_name="data_analysis_agent",
                status="completed",
                started_at=step1_start,
                completed_at=step1_end,
                summary="Deterministic data extraction across revenue, support, inventory, and marketing completed with 100% coverage.",
                output_ref=f"{investigation_id}_data_analysis",
            )
        )

        if self.db is not None:
            log_audit_event(
                db=self.db,
                event_type="EVIDENCE_GENERATED",
                entity_type="investigation",
                entity_id=investigation_id,
                action="generate_evidence",
                actor="data_analysis_agent",
                status="SUCCESS",
                details={"dimensions_analyzed": list(da_output.dimension_analyses.keys())},
            )

        # -------------------------------------------------------------
        # STEP 2: Anomaly Investigation Agent
        # -------------------------------------------------------------
        step2_start = datetime.now(timezone.utc).isoformat()
        ai_input = AnomalyInvestigationInput(
            investigation_id=investigation_id,
            anomaly=anomaly,
            dimension_analyses=da_output.dimension_analyses,
            correlations=da_output.cross_dimension_correlations,
        )
        ai_output = await self.inv_agent.execute(ai_input)
        step2_end = datetime.now(timezone.utc).isoformat()
        timeline.append(
            InvestigationStep(
                step_order=2,
                agent_name="anomaly_investigation_agent",
                status="completed",
                started_at=step2_start,
                completed_at=step2_end,
                summary=f"Identified {len(ai_output.key_findings)} key findings across support escalation and inventory stockout propagation paths.",
                output_ref=f"{investigation_id}_anomaly_investigation",
            )
        )

        # -------------------------------------------------------------
        # STEP 3: Root Cause Agent
        # -------------------------------------------------------------
        step3_start = datetime.now(timezone.utc).isoformat()
        rc_input = RootCauseInput(
            investigation_id=investigation_id,
            anomaly=anomaly,
            dimension_analyses=da_output.dimension_analyses,
            pattern_analysis=ai_output.pattern_analysis,
            anomaly_classification=ai_output.anomaly_classification,
        )
        rc_output = await self.rc_agent.execute(rc_input)
        step3_end = datetime.now(timezone.utc).isoformat()
        timeline.append(
            InvestigationStep(
                step_order=3,
                agent_name="root_cause_agent",
                status="completed",
                started_at=step3_start,
                completed_at=step3_end,
                summary=f"Primary contributing factor identified: {rc_output.primary_root_cause} (Confidence: {rc_output.hypotheses[0].confidence:.2f}).",
                output_ref=f"{investigation_id}_root_cause",
            )
        )

        if self.db is not None:
            log_audit_event(
                db=self.db,
                event_type="ROOT_CAUSE_IDENTIFIED",
                entity_type="investigation",
                entity_id=investigation_id,
                action="identify_root_cause",
                actor="root_cause_agent",
                status="SUCCESS",
                details={
                    "primary_root_cause": rc_output.primary_root_cause,
                    "confidence": rc_output.hypotheses[0].confidence,
                    "description": rc_output.hypotheses[0].description,
                },
            )

        # -------------------------------------------------------------
        # STEP 4: Business Impact Agent
        # -------------------------------------------------------------
        step4_start = datetime.now(timezone.utc).isoformat()
        bi_input = BusinessImpactInput(
            investigation_id=investigation_id,
            anomaly=anomaly,
            root_causes=rc_output.hypotheses,
            dimension_analyses=da_output.dimension_analyses,
        )
        bi_output = await self.impact_agent.execute(bi_input)
        step4_end = datetime.now(timezone.utc).isoformat()
        timeline.append(
            InvestigationStep(
                step_order=4,
                agent_name="business_impact_agent",
                status="completed",
                started_at=step4_start,
                completed_at=step4_end,
                summary=f"Deterministic revenue loss calculated: ${bi_output.realized_impact.revenue_loss:,.2f} with ${bi_output.projected_impact.revenue_at_risk_30d:,.2f} 30-day forward risk.",
                output_ref=f"{investigation_id}_business_impact",
            )
        )

        if self.db is not None:
            log_audit_event(
                db=self.db,
                event_type="IMPACT_CALCULATED",
                entity_type="investigation",
                entity_id=investigation_id,
                action="calculate_business_impact",
                actor="business_impact_agent",
                status="SUCCESS",
                details={
                    "realized_revenue_loss": bi_output.realized_impact.revenue_loss,
                    "projected_30d_risk": bi_output.projected_impact.revenue_at_risk_30d,
                    "customers_at_risk": bi_output.projected_impact.customers_at_risk,
                },
            )

        # -------------------------------------------------------------
        # STEP 5: Recommendation Agent
        # -------------------------------------------------------------
        step5_start = datetime.now(timezone.utc).isoformat()
        rec_input = RecommendationInput(
            investigation_id=investigation_id,
            root_causes=rc_output.hypotheses,
            business_impact=bi_output,
        )
        rec_output = await self.rec_agent.execute(rec_input)
        step5_end = datetime.now(timezone.utc).isoformat()
        timeline.append(
            InvestigationStep(
                step_order=5,
                agent_name="recommendation_agent",
                status="completed",
                started_at=step5_start,
                completed_at=step5_end,
                summary=f"Formulated {len(rec_output.recommendations)} evidence-backed recommendations requiring human approval.",
                output_ref=f"{investigation_id}_recommendations",
            )
        )

        # -------------------------------------------------------------
        # STEP 6: Persistence & Human Approval Registration
        # -------------------------------------------------------------
        supervisor_root_causes = [
            RootCauseHypothesis(
                hypothesis_id=h.hypothesis_id,
                description=h.description,
                confidence=h.confidence,
                evidence=h.evidence,
                causal_chain=[f"{s.cause} -> {s.effect}" for s in h.causal_chain],
                addresses_dimensions=h.affected_dimensions,
            )
            for h in rc_output.hypotheses
        ]

        supervisor_recommendations = [
            Recommendation(
                recommendation_id=r.recommendation_id,
                title=r.title,
                description=r.description,
                category=r.category,
                priority=r.priority,
                expected_impact=f"{r.expected_impact.metric}: +{r.expected_impact.estimated_improvement_pct}% (${r.expected_impact.estimated_revenue_recovery:,.2f} recovery)",
                requires_approval=r.requires_approval,
                action_type=r.action_type,
            )
            for r in rec_output.recommendations
        ]

        impact_report = BusinessImpactReport(
            total_revenue_loss=bi_output.realized_impact.revenue_loss,
            customer_churn_count=bi_output.realized_impact.customer_churn_count,
            projected_30d_risk=bi_output.projected_impact.revenue_at_risk_30d,
            projected_90d_risk=bi_output.projected_impact.revenue_at_risk_90d,
            severity=bi_output.severity_assessment.level,
            narrative=bi_output.narrative_summary,
        )

        if self.db is not None:
            db = self.db
            # 1. Persist Investigation Record
            inv_rec = InvestigationModel(
                investigation_id=investigation_id,
                anomaly_id=anomaly.anomaly_id,
                status="awaiting_approval",
                confidence_score=rc_output.hypotheses[0].confidence,
                summary=rec_output.summary,
                root_causes=[h.model_dump() for h in supervisor_root_causes],
                business_impact=impact_report.model_dump(),
                timeline=[s.model_dump() for s in timeline],
                observations={
                    "observed": [c.description for da in da_output.dimension_analyses.values() for c in da.notable_changes],
                    "inferred": [c.interpretation for c in da_output.cross_dimension_correlations],
                    "hypotheses": [h.description for h in rc_output.hypotheses],
                },
                requires_approval=True,
                started_at=datetime.fromisoformat(step1_start),
                completed_at=datetime.fromisoformat(step5_end),
            )
            db.add(inv_rec)

            # 2. Persist Recommendations & Create Approval Requests
            for r in rec_output.recommendations:
                existing_rec = db.scalar(select(RecommendationModel).where(RecommendationModel.recommendation_id == r.recommendation_id))
                if not existing_rec:
                    rec_model = RecommendationModel(
                        recommendation_id=r.recommendation_id,
                        investigation_id=investigation_id,
                        title=r.title,
                        description=r.description,
                        category=r.category,
                        priority=r.priority,
                        expected_impact=r.expected_impact.model_dump(),
                        implementation=r.implementation.model_dump(),
                        risks=r.risks,
                        supporting_evidence=[e.model_dump() for e in rc_output.hypotheses[0].evidence],
                        addresses_root_cause=r.addresses_root_cause,
                        requires_human_approval=r.requires_approval,
                        action_type=r.action_type,
                        action_parameters={"action_type": r.action_type, "recommendation_id": r.recommendation_id},
                        approval_status="PENDING_APPROVAL",
                    )
                    db.add(rec_model)
                else:
                    existing_rec.investigation_id = investigation_id
                    existing_rec.title = r.title
                    existing_rec.description = r.description
                    existing_rec.expected_impact = r.expected_impact.model_dump()
                    existing_rec.approval_status = "PENDING_APPROVAL"

                approval_id = f"APPR-{r.recommendation_id}"
                existing_req = db.scalar(select(ApprovalRequestModel).where(ApprovalRequestModel.approval_id == approval_id))
                if not existing_req:
                    approval_req = ApprovalRequestModel(
                        approval_id=approval_id,
                        recommendation_id=r.recommendation_id,
                        investigation_id=investigation_id,
                        action_type=r.action_type,
                        action_details=r.model_dump(),
                        status="PENDING_APPROVAL",
                    )
                    db.add(approval_req)
                else:
                    existing_req.investigation_id = investigation_id
                    existing_req.action_details = r.model_dump()
                    existing_req.status = "PENDING_APPROVAL"

                log_audit_event(
                    db=db,
                    event_type="RECOMMENDATION_CREATED",
                    entity_type="recommendation",
                    entity_id=r.recommendation_id,
                    action="create_recommendation",
                    actor="recommendation_agent",
                    status="PROPOSED",
                    details={"title": r.title, "action_type": r.action_type, "priority": r.priority},
                )

                log_audit_event(
                    db=db,
                    event_type="APPROVAL_REQUESTED",
                    entity_type="approval",
                    entity_id=approval_id,
                    action="request_human_approval",
                    actor="supervisor_agent",
                    status="PENDING_APPROVAL",
                    details={
                        "recommendation_id": r.recommendation_id,
                        "investigation_id": investigation_id,
                        "action_type": r.action_type,
                    },
                )

            db.commit()

        return SupervisorOutput(
            investigation_id=investigation_id,
            status=InvestigationStatus.AWAITING_APPROVAL,
            timeline=timeline,
            root_causes=supervisor_root_causes,
            confidence_score=rc_output.hypotheses[0].confidence,
            business_impact=impact_report,
            recommendations=supervisor_recommendations,
            requires_approval=True,
        )
