"""
ORION Provider-Agnostic Agent Runtime Interfaces

Defines the abstract interface for connecting external agentic runtimes (like Adya
or local orchestrators) to ORION's deterministic MCP tool layer.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DecisionTraceItem(BaseModel):
    """A user-facing step in the agent's causal decision progression."""
    stage: str  # OBSERVATION, EVIDENCE, HYPOTHESIS, IMPACT, RECOMMENDATION, RISK, GOVERNANCE, EXECUTION
    title: str
    summary: str
    confidence_score: Optional[float] = None
    risk_level: Optional[str] = None


class ConfidenceScores(BaseModel):
    """Deterministic confidence and risk metrics for an investigation."""
    detection_confidence: float = 0.95
    detection_explanation: str = "Statistical z-score deviation evaluated across 93 days of baseline operations."
    root_cause_confidence: float = 0.88
    root_cause_explanation: str = "Strong cross-signal temporal alignment between support backlog and inventory stockouts."
    recommendation_confidence: float = 0.91
    recommendation_explanation: str = "Deterministic capacity model projects 78% backlog reduction within 7 operational days."
    action_risk: str = "MEDIUM"
    action_risk_explanation: str = "Operational capacity shift; fully reversible via simulated rollback procedure."


class GovernanceDetails(BaseModel):
    """Structured governance requirements for human authorization gate."""
    action: str = "Support Team Capacity Escalation & SLA Remediation"
    risk_level: str = "MEDIUM"
    affected_system: str = "NovaCart Zendesk Queue & Operations Roster"
    affected_scope: str = "15 Support Specialists / Tier-2 Triage Routing"
    parameters: Dict[str, Any] = Field(default_factory=lambda: {"agents_to_add": 15, "routing_mode": "urgent_triage"})
    expected_benefit: str = "Reduces support resolution latency from 26.5h to <4.0h and mitigates $5.09M forward churn risk."
    potential_risk: str = "Short-term onboarding queue overhead; fully reversible with zero persistent data corruption."
    why_approval_required: str = "Operational budget reallocation exceeds automated governance threshold ($25,000 limit)."


class AgentTraceStep(BaseModel):
    """A discrete step in an agentic orchestration trace."""
    step_id: int
    timestamp: str
    agent_role: str
    tool_called: str
    tool_safety: str
    input_summary: str
    output_summary: str
    status: str  # PENDING, RUNNING, COMPLETED, WAITING_FOR_APPROVAL, BLOCKED, FAILED
    duration_ms: float = 0.0
    evidence_type: Optional[str] = None  # OBSERVED, INFERRED, HYPOTHESIS, PROPOSAL, ACTION_RESULT
    details: Dict[str, Any] = Field(default_factory=dict)


class AgentRunTrace(BaseModel):
    """Complete trace record of an autonomous agent investigation run."""
    run_id: str
    anomaly_id: str
    scenario_title: Optional[str] = None
    status: str  # INITIALIZED, RUNNING, WAITING_FOR_APPROVAL, COMPLETED, REJECTED, FAILED
    started_at: str
    completed_at: Optional[str] = None
    steps: List[AgentTraceStep] = Field(default_factory=list)
    decision_trace: List[DecisionTraceItem] = Field(default_factory=list)
    scores: Optional[ConfidenceScores] = None
    governance_details: Optional[GovernanceDetails] = None
    active_recommendation_id: Optional[str] = None
    approval_request_id: Optional[str] = None
    approval_status: Optional[str] = None
    simulation_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentRuntimeProvider(ABC):
    """
    Abstract interface for Agent Runtime Providers.

    Allows ORION to be driven by:
    - LocalAgentRuntime (included in Milestone 6A)
    - AdyaAgentRuntime (future integration point for Milestone 6B)
    - Custom external LLM / Autonomous Agent Runtimes
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the unique identifier of the agent runtime provider."""
        pass

    @abstractmethod
    def discover_tools(self) -> Dict[str, str]:
        """Discover available MCP tools and their safety classifications."""
        pass

    @abstractmethod
    def start_agent_run(self, anomaly_id: str = "ANOM-REV-001") -> AgentRunTrace:
        """Initiate an autonomous agent investigation run up to human approval gate."""
        pass

    @abstractmethod
    def approve_and_execute(
        self,
        run_id: str,
        recommendation_id: str,
        approver: str = "ExecutiveOperationsVP",
        reason: str = "Approved via Executive Operations Console",
    ) -> AgentRunTrace:
        """Process human approval and execute safe operational simulation."""
        pass

    @abstractmethod
    def reject_run(
        self,
        run_id: str,
        recommendation_id: str,
        rejector: str = "ExecutiveOperationsVP",
        reason: str = "Rejected during executive review",
    ) -> AgentRunTrace:
        """Process human rejection and permanently block execution."""
        pass

    @abstractmethod
    def get_run_trace(self, run_id: str) -> Optional[AgentRunTrace]:
        """Retrieve trace for a specific agent run."""
        pass

    @abstractmethod
    def get_all_runs(self) -> List[AgentRunTrace]:
        """Retrieve all historical agent runs."""
        pass
