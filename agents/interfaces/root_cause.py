"""
RootCauseAgent Interface

Generates ranked root-cause hypotheses based on evidence from
upstream agents. Each hypothesis must cite specific data points.

CRITICAL: Confidence scores are derived from statistical evidence
strength, NOT from LLM self-assessment.
"""

from typing import Type

from pydantic import BaseModel, Field

from .base import AnomalyRecord, BaseAgent, EvidenceItem
from .anomaly_investigation import AnomalyClassification, PatternAnalysis
from .data_analysis import DimensionAnalysis


# ---------------------------------------------------------------------------
# Output Sub-Schemas
# ---------------------------------------------------------------------------

class CausalStep(BaseModel):
    """A single step in a causal chain."""
    step_order: int
    cause: str
    effect: str
    mechanism: str
    evidence: list[EvidenceItem]
    time_lag: str | None = None


class RootCauseHypothesis(BaseModel):
    """A ranked root-cause hypothesis with evidence."""
    hypothesis_id: str
    description: str
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Derived from statistical evidence, not LLM opinion",
    )
    evidence: list[EvidenceItem]
    causal_chain: list[CausalStep]
    alternative_explanations: list[str]
    affected_dimensions: list[str]


class EvidenceStrengthReport(BaseModel):
    """Overall assessment of evidence quality."""
    total_evidence_items: int
    strong_evidence_count: int
    moderate_evidence_count: int
    weak_evidence_count: int
    data_gaps: list[str]
    overall_strength: str = Field(
        ..., description="strong | moderate | weak | insufficient"
    )


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class RootCauseInput(BaseModel):
    """Input to the RootCauseAgent."""
    investigation_id: str
    anomaly: AnomalyRecord
    dimension_analyses: dict[str, DimensionAnalysis]
    pattern_analysis: PatternAnalysis
    anomaly_classification: AnomalyClassification


class RootCauseOutput(BaseModel):
    """Output from the RootCauseAgent."""
    investigation_id: str
    hypotheses: list[RootCauseHypothesis]
    primary_root_cause: str = Field(
        ..., description="hypothesis_id of highest-confidence hypothesis"
    )
    evidence_strength: EvidenceStrengthReport


# ---------------------------------------------------------------------------
# Agent Interface
# ---------------------------------------------------------------------------

class RootCauseAgent(BaseAgent):
    """
    Generates ranked root-cause hypotheses from evidence.

    Confidence scores are computed from statistical evidence
    strength — correlation coefficients, p-values, effect sizes —
    not from the LLM's self-assessed certainty.
    """

    @property
    def name(self) -> str:
        return "root_cause_agent"

    @property
    def description(self) -> str:
        return (
            "Generates ranked root-cause hypotheses with cited evidence "
            "and statistically-derived confidence scores."
        )

    @property
    def input_schema(self) -> Type[BaseModel]:
        return RootCauseInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return RootCauseOutput

    @property
    def tools(self) -> list[str]:
        return [
            "query_revenue_metrics",
            "query_support_metrics",
            "query_customer_metrics",
            "compute_correlation",
            "compute_statistical_tests",
        ]

    async def execute(self, input_data: RootCauseInput) -> RootCauseOutput:
        raise NotImplementedError("Implement in concrete provider class")

    async def validate_output(self, output: RootCauseOutput) -> bool:
        if not output.hypotheses:
            return False
        # Every hypothesis must have evidence
        for h in output.hypotheses:
            if not h.evidence:
                return False
            if not h.causal_chain:
                return False
        # Primary must reference a valid hypothesis
        ids = {h.hypothesis_id for h in output.hypotheses}
        if output.primary_root_cause not in ids:
            return False
        return True
