"""
RecommendationAgent Interface

Generates prioritized action recommendations based on root causes
and business impact. Each recommendation includes expected impact,
implementation difficulty, and time-to-effect.
"""

from typing import Type

from pydantic import BaseModel, Field

from .base import BaseAgent
from .business_impact import BusinessImpactOutput
from .data_analysis import MetricSummary
from .root_cause import RootCauseHypothesis


# ---------------------------------------------------------------------------
# Output Sub-Schemas
# ---------------------------------------------------------------------------

class ExpectedImpact(BaseModel):
    """Expected impact of implementing a recommendation."""
    metric: str
    estimated_improvement_pct: float
    estimated_revenue_recovery: float | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    time_to_effect_days: int


class ImplementationDetails(BaseModel):
    """Details on implementing a recommendation."""
    difficulty: str = Field(..., description="low | medium | high")
    estimated_cost: float | None = None
    prerequisites: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    """A single action recommendation."""
    recommendation_id: str
    title: str
    description: str
    category: str = Field(..., description="immediate | short_term | long_term")
    priority: int = Field(..., ge=1)
    expected_impact: ExpectedImpact
    implementation: ImplementationDetails
    risks: list[str] = Field(default_factory=list)
    addresses_root_cause: str = Field(
        ..., description="hypothesis_id this recommendation addresses"
    )
    requires_approval: bool = True
    action_type: str = Field(
        ..., description="Maps to ActionAgent capability"
    )


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class RecommendationInput(BaseModel):
    """Input to the RecommendationAgent."""
    investigation_id: str
    root_causes: list[RootCauseHypothesis]
    business_impact: BusinessImpactOutput
    current_metrics: dict[str, MetricSummary] = Field(default_factory=dict)


class RecommendationOutput(BaseModel):
    """Output from the RecommendationAgent."""
    investigation_id: str
    recommendations: list[Recommendation]
    summary: str = Field(
        ..., description="Executive summary of recommended actions"
    )


# ---------------------------------------------------------------------------
# Agent Interface
# ---------------------------------------------------------------------------

class RecommendationAgent(BaseAgent):
    """
    Generates prioritized action recommendations.

    Recommendations are grounded in root-cause evidence and
    quantified business impact. Each recommendation maps to
    a concrete action type that ActionAgent can execute.
    """

    @property
    def name(self) -> str:
        return "recommendation_agent"

    @property
    def description(self) -> str:
        return (
            "Generates prioritized, actionable recommendations based on "
            "root-cause analysis and quantified business impact."
        )

    @property
    def input_schema(self) -> Type[BaseModel]:
        return RecommendationInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return RecommendationOutput

    @property
    def tools(self) -> list[str]:
        return [
            "query_revenue_metrics",
            "query_support_metrics",
            "query_inventory_metrics",
        ]

    async def execute(
        self, input_data: RecommendationInput
    ) -> RecommendationOutput:
        raise NotImplementedError("Implement in concrete provider class")

    async def validate_output(self, output: RecommendationOutput) -> bool:
        if not output.recommendations:
            return False
        # Must have at least one immediate recommendation
        categories = {r.category for r in output.recommendations}
        if "immediate" not in categories:
            return False
        # Priorities must be sequential starting at 1
        priorities = sorted(r.priority for r in output.recommendations)
        if priorities[0] != 1:
            return False
        return True
