"""
AnomalyInvestigationAgent Interface

Analyzes anomaly patterns across structured data produced by
DataAnalysisAgent. Identifies temporal patterns, correlations,
and anomaly propagation paths.

This agent INTERPRETS pre-computed statistical results.
It does NOT compute statistics or generate numbers.
"""

from typing import Type

from pydantic import BaseModel, Field

from .base import AnomalyRecord, BaseAgent, EvidenceItem
from .data_analysis import Correlation, DimensionAnalysis


# ---------------------------------------------------------------------------
# Output Sub-Schemas
# ---------------------------------------------------------------------------

class TemporalPattern(BaseModel):
    """A pattern observed over time."""
    pattern_type: str = Field(
        ..., description="e.g. 'gradual_decline', 'sudden_drop', 'cyclical'"
    )
    description: str
    onset_date: str
    affected_metrics: list[str]
    evidence: list[EvidenceItem]


class CorrelationNarrative(BaseModel):
    """Human-readable interpretation of a statistical correlation."""
    metric_a: str
    metric_b: str
    correlation: float
    narrative: str = Field(
        ..., description="Agent's interpretation of what this correlation means"
    )
    potential_causation: bool
    confidence_note: str = ""


class PropagationStep(BaseModel):
    """A step in the anomaly propagation path."""
    step_order: int
    source_dimension: str
    target_dimension: str
    mechanism: str = Field(
        ..., description="How the anomaly propagated between dimensions"
    )
    time_lag_days: int | None = None
    evidence: list[EvidenceItem]


class OnsetAnalysis(BaseModel):
    """Analysis of when and how the anomaly began."""
    estimated_onset: str
    onset_type: str = Field(
        ..., description="sudden | gradual | periodic"
    )
    trigger_candidates: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)


class AnomalyClassification(BaseModel):
    """Classification of the anomaly type."""
    anomaly_type: str = Field(
        ..., description="systemic | localized | seasonal | external"
    )
    affected_dimensions: list[str]
    onset_analysis: OnsetAnalysis
    scope_description: str


class Finding(BaseModel):
    """A key finding from the investigation."""
    finding_id: str
    title: str
    description: str
    severity: str
    evidence: list[EvidenceItem]
    related_dimensions: list[str]


class PatternAnalysis(BaseModel):
    """Complete pattern analysis output."""
    temporal_patterns: list[TemporalPattern]
    correlation_narratives: list[CorrelationNarrative]
    propagation_path: list[PropagationStep]


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class AnomalyInvestigationInput(BaseModel):
    """Input to the AnomalyInvestigationAgent."""
    investigation_id: str
    anomaly: AnomalyRecord
    dimension_analyses: dict[str, DimensionAnalysis]
    correlations: list[Correlation]


class AnomalyInvestigationOutput(BaseModel):
    """Output from the AnomalyInvestigationAgent."""
    investigation_id: str
    pattern_analysis: PatternAnalysis
    anomaly_classification: AnomalyClassification
    key_findings: list[Finding]


# ---------------------------------------------------------------------------
# Agent Interface
# ---------------------------------------------------------------------------

class AnomalyInvestigationAgent(BaseAgent):
    """
    Investigates anomaly patterns across pre-computed data.

    Interprets statistical results to identify patterns a human
    analyst would look for. Does NOT compute statistics.
    """

    @property
    def name(self) -> str:
        return "anomaly_investigation_agent"

    @property
    def description(self) -> str:
        return (
            "Analyzes anomaly patterns, temporal correlations, and "
            "propagation paths across pre-computed business data."
        )

    @property
    def input_schema(self) -> Type[BaseModel]:
        return AnomalyInvestigationInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return AnomalyInvestigationOutput

    @property
    def tools(self) -> list[str]:
        return [
            "query_revenue_metrics",
            "query_support_metrics",
            "query_inventory_metrics",
            "compute_correlation",
        ]

    async def execute(
        self, input_data: AnomalyInvestigationInput
    ) -> AnomalyInvestigationOutput:
        raise NotImplementedError("Implement in concrete provider class")

    async def validate_output(
        self, output: AnomalyInvestigationOutput
    ) -> bool:
        if not output.key_findings:
            return False
        if not output.anomaly_classification.affected_dimensions:
            return False
        return True
