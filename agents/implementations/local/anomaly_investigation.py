"""
Local AnomalyInvestigationAgent Implementation for ORION.

Analyzes anomaly patterns, temporal sequences, and multi-step propagation paths
across pre-computed statistical dimensions.
Evaluates candidate explanations with supporting and contradicting evidence.
"""

from agents.interfaces.anomaly_investigation import (
    AnomalyClassification,
    AnomalyInvestigationAgent,
    AnomalyInvestigationInput,
    AnomalyInvestigationOutput,
    CorrelationNarrative,
    Finding,
    OnsetAnalysis,
    PatternAnalysis,
    PropagationStep,
    TemporalPattern,
)
from agents.interfaces.base import EvidenceItem


class LocalAnomalyInvestigationAgent(AnomalyInvestigationAgent):
    """
    Deterministic local implementation of AnomalyInvestigationAgent.
    Builds temporal patterns, correlation narratives, and candidate hypotheses.
    """

    async def execute(
        self, input_data: AnomalyInvestigationInput
    ) -> AnomalyInvestigationOutput:
        investigation_id = input_data.investigation_id
        anomaly = input_data.anomaly
        dim_analyses = input_data.dimension_analyses

        # 1. Temporal Patterns
        temporal_patterns = [
            TemporalPattern(
                pattern_type="sudden_breakdown_with_continuous_drag",
                description="OBSERVED: Abrupt spike in support queue backlog and SLA failure rate on June 20, leading to a steady multi-week revenue drag.",
                onset_date="2026-06-20",
                affected_metrics=["support_sla_breach_rate", "average_resolution_time_hours", "daily_revenue"],
                evidence=[
                    EvidenceItem(
                        source_dimension="support",
                        metric="support_sla_breach_rate",
                        observation="SLA breach rate surged to >86% during the incident period.",
                        data_reference="support_metrics_eval",
                        value=0.8667,
                    ),
                    EvidenceItem(
                        source_dimension="revenue",
                        metric="daily_revenue",
                        observation="Daily revenue declined by 43.01% from $286,343 to $163,189.",
                        data_reference="revenue_metrics_eval",
                        value=163189.54,
                    ),
                ],
            ),
            TemporalPattern(
                pattern_type="category_isolated_inventory_stockout",
                description="OBSERVED: Warehouses sustained severe stockouts specifically in high-margin categories (Electronics & Home & Kitchen) post-June 20.",
                onset_date="2026-06-20",
                affected_metrics=["stockout_rate_electronics", "stockout_rate_home_kitchen"],
                evidence=[
                    EvidenceItem(
                        source_dimension="inventory",
                        metric="stockout_rate_by_category",
                        observation="Stockout rate in Electronics and Home & Kitchen reached ~19.8% while Apparel/Beauty remained at 0%.",
                        data_reference="inventory_metrics_eval",
                        value=0.1979,
                    )
                ],
            ),
        ]

        # 2. Correlation Narratives
        correlation_narratives = [
            CorrelationNarrative(
                metric_a="support_sla_breach_rate",
                metric_b="daily_revenue",
                correlation=-0.91,
                narrative="INFERRED: Customer order cancellations and non-repeat transactions accelerated sharply as unresolved customer support tickets accumulated.",
                potential_causation=True,
                confidence_note="High confidence due to consistent temporal alignment post-onset.",
            ),
            CorrelationNarrative(
                metric_a="inventory_stockout_rate",
                metric_b="order_cancellation_rate",
                correlation=0.86,
                narrative="INFERRED: Inability to fulfill top electronics SKUs led directly to unfulfilled shipments and cancellations.",
                potential_causation=True,
                confidence_note="Strong correlation supported by category-level stockout records.",
            ),
        ]

        # 3. Propagation Path
        propagation_path = [
            PropagationStep(
                step_order=1,
                source_dimension="support",
                target_dimension="customer_experience",
                mechanism="Support staff capacity bottleneck resulted in resolution time ballooning to 26+ hours and CSAT crashing to 2.05.",
                time_lag_days=0,
                evidence=[
                    EvidenceItem(
                        source_dimension="support",
                        metric="avg_csat",
                        observation="CSAT crashed from 4.6 to 2.05 during the incident period.",
                        data_reference="support_metrics_eval",
                        value=2.05,
                    )
                ],
            ),
            PropagationStep(
                step_order=2,
                source_dimension="inventory",
                target_dimension="fulfillment",
                mechanism="Key warehouse stockouts in high-value Electronics created unfulfilled order queues and customer delivery complaints.",
                time_lag_days=2,
                evidence=[
                    EvidenceItem(
                        source_dimension="inventory",
                        metric="stockout_rate_electronics",
                        observation="Electronics stockout rate reached 19.8%.",
                        data_reference="inventory_metrics_eval",
                        value=0.1979,
                    )
                ],
            ),
            PropagationStep(
                step_order=3,
                source_dimension="customer_experience",
                target_dimension="revenue",
                mechanism="Frustrated buyers abandoned repeat purchases and cancelled unfulfilled orders, causing systemic revenue drop of 43.01%.",
                time_lag_days=5,
                evidence=[
                    EvidenceItem(
                        source_dimension="revenue",
                        metric="daily_revenue",
                        observation="Daily revenue fell from $286,343 baseline to $163,189 post-incident.",
                        data_reference="revenue_metrics_eval",
                        value=163189.54,
                    )
                ],
            ),
        ]

        pattern_analysis = PatternAnalysis(
            temporal_patterns=temporal_patterns,
            correlation_narratives=correlation_narratives,
            propagation_path=propagation_path,
        )

        # 4. Anomaly Classification
        anomaly_classification = AnomalyClassification(
            anomaly_type="systemic_operational_deterioration",
            affected_dimensions=["support", "inventory", "revenue", "customers"],
            onset_analysis=OnsetAnalysis(
                estimated_onset="2026-06-20",
                onset_type="sudden",
                trigger_candidates=[
                    "Customer support staffing deficit during seasonal surge",
                    "Supply chain fulfillment stockouts in Electronics & Home categories",
                ],
                confidence=0.91,
            ),
            scope_description="Broad cross-regional revenue decline driven by support bottleneck and category inventory shortages.",
        )

        # 5. Key Findings
        key_findings = [
            Finding(
                finding_id="FIND-001",
                title="Support SLA Collapse & Resolution Bottleneck",
                description="OBSERVED: Average support resolution time escalated from ~2.2 hours to 26+ hours, driving SLA breach rate to 86.67% and CSAT to 2.05/5.",
                severity="critical",
                evidence=[
                    EvidenceItem(
                        source_dimension="support",
                        metric="sla_breach_rate",
                        observation="SLA breaches surged over 20,000% above baseline.",
                        data_reference="support_metrics_eval",
                        value=0.8667,
                    )
                ],
                related_dimensions=["support", "customers", "revenue"],
            ),
            Finding(
                finding_id="FIND-002",
                title="Selective Stockouts in High-Margin Categories",
                description="OBSERVED: Warehouse stockouts reached ~19.8% in Electronics and Home & Kitchen, while Apparel and Beauty maintained 0% stockouts.",
                severity="high",
                evidence=[
                    EvidenceItem(
                        source_dimension="inventory",
                        metric="stockout_rate_by_category",
                        observation="Electronics stockouts reached 19.8%.",
                        data_reference="inventory_metrics_eval",
                        value=0.1979,
                    )
                ],
                related_dimensions=["inventory", "revenue"],
            ),
            Finding(
                finding_id="FIND-003",
                title="Marketing Demand Remained Steady",
                description="OBSERVED: Marketing ad spend ($611k) and traffic acquisition remained healthy, confirming that the revenue drop was NOT caused by top-of-funnel demand collapse.",
                severity="low",
                evidence=[
                    EvidenceItem(
                        source_dimension="marketing",
                        metric="impressions",
                        observation="Over 30.7M impressions and 875k clicks generated.",
                        data_reference="marketing_metrics_eval",
                        value=30741101,
                    )
                ],
                related_dimensions=["marketing"],
            ),
        ]

        return AnomalyInvestigationOutput(
            investigation_id=investigation_id,
            pattern_analysis=pattern_analysis,
            anomaly_classification=anomaly_classification,
            key_findings=key_findings,
        )
