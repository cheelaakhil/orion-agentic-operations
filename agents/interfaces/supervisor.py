"""
SupervisorAgent Interface

Orchestrates the investigation pipeline. In v1 this is implemented as a
deterministic state machine. When Adya is integrated, it becomes an
LLM-driven orchestrator.
"""

from enum import Enum
from typing import Any, Type

from pydantic import BaseModel, Field

from .base import (
    AnomalyRecord,
    BaseAgent,
    EvidenceItem,
    Severity,
    TimeRange,
)


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class InvestigationConfig(BaseModel):
    """Optional overrides for investigation behavior."""
    dimensions: list[str] = Field(
        default=[
            "revenue", "regions", "products", "customers",
            "customer_segments", "repeat_purchases", "inventory",
            "support_tickets", "support_sla", "marketing",
        ],
        description="Dimensions to investigate",
    )
    time_range: TimeRange | None = None
    max_hypotheses: int = Field(default=5, ge=1, le=20)
    timeout_seconds: int = Field(default=120, ge=10)


class InvestigationStatus(str, Enum):
    """Status of an investigation."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING_ACTIONS = "executing_actions"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestigationStep(BaseModel):
    """A single step in the investigation timeline."""
    step_order: int
    agent_name: str
    status: str
    started_at: str
    completed_at: str | None = None
    summary: str | None = None
    output_ref: str | None = Field(
        default=None, description="Reference to stored output"
    )


class RootCauseHypothesis(BaseModel):
    """A ranked root-cause hypothesis."""
    hypothesis_id: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: list[EvidenceItem]
    causal_chain: list[str]
    addresses_dimensions: list[str]


class BusinessImpactReport(BaseModel):
    """Quantified business impact summary."""
    total_revenue_loss: float
    customer_churn_count: int
    projected_30d_risk: float
    projected_90d_risk: float
    severity: Severity
    narrative: str


class Recommendation(BaseModel):
    """A recommended action."""
    recommendation_id: str
    title: str
    description: str
    category: str = Field(..., description="immediate | short_term | long_term")
    priority: int = Field(..., ge=1)
    expected_impact: str
    requires_approval: bool = True
    action_type: str


class SupervisorInput(BaseModel):
    """Input to the SupervisorAgent."""
    anomaly: AnomalyRecord
    config: InvestigationConfig = Field(default_factory=InvestigationConfig)


class SupervisorOutput(BaseModel):
    """Output from the SupervisorAgent."""
    investigation_id: str
    status: InvestigationStatus
    timeline: list[InvestigationStep]
    root_causes: list[RootCauseHypothesis]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    business_impact: BusinessImpactReport
    recommendations: list[Recommendation]
    requires_approval: bool


# ---------------------------------------------------------------------------
# Agent Interface
# ---------------------------------------------------------------------------

class SupervisorAgent(BaseAgent):
    """
    Orchestrates the full investigation pipeline.

    Pipeline order:
      1. DataAnalysisAgent
      2. AnomalyInvestigationAgent
      3. RootCauseAgent
      4. BusinessImpactAgent
      5. RecommendationAgent
      6. [Human Approval]
      7. ActionAgent
    """

    @property
    def name(self) -> str:
        return "supervisor_agent"

    @property
    def description(self) -> str:
        return (
            "Orchestrates the investigation pipeline, coordinating "
            "specialized agents to investigate anomalies end-to-end."
        )

    @property
    def input_schema(self) -> Type[BaseModel]:
        return SupervisorInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return SupervisorOutput

    @property
    def tools(self) -> list[str]:
        return []  # Supervisor orchestrates; it doesn't call MCP tools directly

    async def execute(self, input_data: SupervisorInput) -> SupervisorOutput:
        raise NotImplementedError("Implement in concrete provider class")

    async def validate_output(self, output: SupervisorOutput) -> bool:
        """Validate investigation completeness."""
        if not output.timeline:
            return False
        if not output.root_causes:
            return False
        if output.confidence_score < 0 or output.confidence_score > 1:
            return False
        return True
