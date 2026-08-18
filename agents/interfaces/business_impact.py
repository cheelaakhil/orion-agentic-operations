"""
BusinessImpactAgent Interface

Quantifies the business impact of identified root causes.
All financial calculations are deterministic — the agent adds
narrative context and projections methodology description.
"""

from typing import Type

from pydantic import BaseModel, Field

from .base import AnomalyRecord, BaseAgent, Severity, TimeRange
from .data_analysis import DimensionAnalysis
from .root_cause import RootCauseHypothesis


# ---------------------------------------------------------------------------
# Output Sub-Schemas
# ---------------------------------------------------------------------------

class RealizedImpact(BaseModel):
    """Quantified impact that has already occurred (deterministic)."""
    revenue_loss: float = Field(..., description="Computed by SQL, not LLM")
    order_count_decline: int
    customer_churn_count: int
    support_cost_increase: float
    period: TimeRange


class ProjectedImpact(BaseModel):
    """Projected future impact (deterministic model)."""
    revenue_at_risk_30d: float
    revenue_at_risk_90d: float
    customers_at_risk: int
    methodology: str = Field(
        ..., description="Description of projection method used"
    )


class DimensionImpact(BaseModel):
    """Impact breakdown for a single dimension."""
    dimension: str
    metric: str
    realized_loss: float
    projected_loss_30d: float
    description: str


class SeverityAssessment(BaseModel):
    """Overall severity assessment with justification."""
    level: Severity
    justification: str
    requires_immediate_action: bool


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class BusinessImpactInput(BaseModel):
    """Input to the BusinessImpactAgent."""
    investigation_id: str
    anomaly: AnomalyRecord
    root_causes: list[RootCauseHypothesis]
    dimension_analyses: dict[str, DimensionAnalysis]


class BusinessImpactOutput(BaseModel):
    """Output from the BusinessImpactAgent."""
    investigation_id: str
    realized_impact: RealizedImpact
    projected_impact: ProjectedImpact
    impact_by_dimension: dict[str, DimensionImpact]
    severity_assessment: SeverityAssessment
    narrative_summary: str = Field(
        ..., description="Agent-generated narrative contextualizing the numbers"
    )


# ---------------------------------------------------------------------------
# Agent Interface
# ---------------------------------------------------------------------------

class BusinessImpactAgent(BaseAgent):
    """
    Quantifies business impact of root causes.

    Financial calculations are deterministic (SQL/Python).
    The agent provides narrative context and methodology
    descriptions around the computed numbers.
    """

    @property
    def name(self) -> str:
        return "business_impact_agent"

    @property
    def description(self) -> str:
        return (
            "Quantifies realized and projected business impact using "
            "deterministic calculations, with agent-generated narrative."
        )

    @property
    def input_schema(self) -> Type[BaseModel]:
        return BusinessImpactInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return BusinessImpactOutput

    @property
    def tools(self) -> list[str]:
        return [
            "query_revenue_metrics",
            "query_customer_metrics",
            "compute_revenue_projection",
            "compute_churn_projection",
        ]

    async def execute(
        self, input_data: BusinessImpactInput
    ) -> BusinessImpactOutput:
        raise NotImplementedError("Implement in concrete provider class")

    async def validate_output(self, output: BusinessImpactOutput) -> bool:
        if output.realized_impact.revenue_loss == 0:
            return False  # Investigation was triggered — there must be impact
        if not output.narrative_summary:
            return False
        return True
