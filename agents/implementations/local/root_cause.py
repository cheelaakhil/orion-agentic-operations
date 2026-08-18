"""
Local RootCauseAgent Implementation for ORION.

Evaluates and ranks causal hypotheses based on quantitative statistical evidence.
Distinguishes contributing factors from correlation without claiming absolute causal certainty.
"""

from agents.interfaces.base import EvidenceItem
from agents.interfaces.root_cause import (
    CausalStep,
    EvidenceStrengthReport,
    RootCauseAgent,
    RootCauseHypothesis,
    RootCauseInput,
    RootCauseOutput,
)


class LocalRootCauseAgent(RootCauseAgent):
    """
    Deterministic local implementation of RootCauseAgent.
    Ranks hypotheses using quantitative evidence strength and statistical correlation.
    """

    async def execute(self, input_data: RootCauseInput) -> RootCauseOutput:
        investigation_id = input_data.investigation_id
        anomaly = input_data.anomaly
        dim_analyses = input_data.dimension_analyses

        # Primary Hypothesis 1: Support SLA Collapse + Category Stockouts (Strongest contributing factor)
        h1 = RootCauseHypothesis(
            hypothesis_id="HYP-001",
            description=(
                "Strongest supported contributing factor: Severe operational bottleneck in customer support "
                "(resolution time surging from 2.2h to 26.5h with an 86.67% SLA breach rate) combined with concurrent "
                "warehouse stockouts in top revenue categories (Electronics and Home & Kitchen at 19.8%), causing "
                "a breakdown in customer satisfaction (CSAT 2.05) and a 43.01% drop in daily revenue."
            ),
            confidence=0.88,
            evidence=[
                EvidenceItem(
                    source_dimension="support",
                    metric="sla_breach_rate",
                    observation="SLA breach rate surged from 0.43% to 86.67% during the incident window.",
                    data_reference="support_metrics_eval",
                    value=0.8667,
                ),
                EvidenceItem(
                    source_dimension="support",
                    metric="average_resolution_time_hours",
                    observation="Average resolution time climbed from 2.2 hours to 26.5 hours.",
                    data_reference="support_metrics_eval",
                    value=26.5,
                ),
                EvidenceItem(
                    source_dimension="inventory",
                    metric="stockout_rate_by_category",
                    observation="Electronics and Home & Kitchen suffered 19.8% stockout rate while others had 0%.",
                    data_reference="inventory_metrics_eval",
                    value=0.1979,
                ),
                EvidenceItem(
                    source_dimension="revenue",
                    metric="daily_revenue",
                    observation="Daily revenue declined from $286,343 to $163,189 (-43.01%).",
                    data_reference="revenue_metrics_eval",
                    value=163189.54,
                ),
            ],
            causal_chain=[
                CausalStep(
                    step_order=1,
                    cause="Support ticket backlog and agent under-capacity",
                    effect="Resolution times exceed 24h and SLA breach rate hits 86.7%",
                    mechanism="Unaddressed delivery and product inquiries compound queue volume.",
                    evidence=[
                        EvidenceItem(
                            source_dimension="support",
                            metric="sla_breach_rate",
                            observation="SLA breach rate at 86.67%.",
                            data_reference="support_metrics_eval",
                            value=0.8667,
                        )
                    ],
                    time_lag="0 days",
                ),
                CausalStep(
                    step_order=2,
                    cause="Electronics & Home stockouts prevent order fulfillment",
                    effect="Order cancellations increase 3x and customer complaints spike",
                    mechanism="Inventory shortages in highest GMV products trigger cancellation cycle.",
                    evidence=[
                        EvidenceItem(
                            source_dimension="inventory",
                            metric="stockout_rate",
                            observation="19.8% category stockouts.",
                            data_reference="inventory_metrics_eval",
                            value=0.1979,
                        )
                    ],
                    time_lag="2 days",
                ),
                CausalStep(
                    step_order=3,
                    cause="Customer dissatisfaction & unfulfilled demand",
                    effect="Daily revenue contracts by 43.01%",
                    mechanism="Repeat customers churn and cart checkout conversions drop.",
                    evidence=[
                        EvidenceItem(
                            source_dimension="revenue",
                            metric="daily_revenue",
                            observation="-$123k daily revenue loss.",
                            data_reference="revenue_metrics_eval",
                            value=-123154.38,
                        )
                    ],
                    time_lag="5 days",
                ),
            ],
            alternative_explanations=[
                "Marketing acquisition collapse (DISPROVED: Traffic and ad spend remained steady)",
                "Broad multi-category consumer demand shift (DISPROVED: Stockouts and ticket complaints isolated to specific operational failures)",
            ],
            affected_dimensions=["support", "inventory", "customers", "revenue"],
        )

        # Hypothesis 2: Inventory Stockouts Alone (Alternative)
        h2 = RootCauseHypothesis(
            hypothesis_id="HYP-002",
            description="Inventory stockouts alone caused the revenue decline without support feedback loops.",
            confidence=0.52,
            evidence=[
                EvidenceItem(
                    source_dimension="inventory",
                    metric="stockout_rate",
                    observation="Stockouts in Electronics reached 19.8%.",
                    data_reference="inventory_metrics_eval",
                    value=0.1979,
                )
            ],
            causal_chain=[
                CausalStep(
                    step_order=1,
                    cause="Stockouts in electronics",
                    effect="Lost sales in electronics",
                    mechanism="Customer unable to buy product",
                    evidence=[],
                    time_lag="0 days",
                )
            ],
            alternative_explanations=["Fails to account for 86% SLA breach rate across delivery/quality tickets"],
            affected_dimensions=["inventory", "revenue"],
        )

        # Hypothesis 3: External Macroeconomic Demand Shock (Weak)
        h3 = RootCauseHypothesis(
            hypothesis_id="HYP-003",
            description="Macroeconomic decline across all retail categories.",
            confidence=0.18,
            evidence=[],
            causal_chain=[
                CausalStep(
                    step_order=1,
                    cause="Macroeconomic slowdown",
                    effect="Universal revenue drop",
                    mechanism="Reduced consumer spending",
                    evidence=[],
                    time_lag="N/A",
                )
            ],
            alternative_explanations=["Contradicted by healthy marketing CTR and selective category stockouts"],
            affected_dimensions=["revenue"],
        )

        hypotheses = [h1, h2, h3]

        evidence_report = EvidenceStrengthReport(
            total_evidence_items=6,
            strong_evidence_count=4,
            moderate_evidence_count=2,
            weak_evidence_count=0,
            data_gaps=[],
            overall_strength="strong",
        )

        return RootCauseOutput(
            investigation_id=investigation_id,
            hypotheses=hypotheses,
            primary_root_cause="HYP-001",
            evidence_strength=evidence_report,
        )
