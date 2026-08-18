"""
ORION Provider-Agnostic Agent Runtime Interfaces

Defines the abstract interface for connecting external agentic runtimes (like Adya
or local orchestrators) to ORION's deterministic MCP tool layer.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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
    status: str  # INITIALIZED, RUNNING, WAITING_FOR_APPROVAL, COMPLETED, REJECTED, FAILED
    started_at: str
    completed_at: Optional[str] = None
    steps: List[AgentTraceStep] = Field(default_factory=list)
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
        """Start an autonomous multi-agent run up to the human approval gate."""
        pass

    @abstractmethod
    def approve_and_execute(
        self,
        run_id: str,
        recommendation_id: str,
        approver: str = "ExecutiveOperationsVP",
        reason: str = "Approved via Executive Operations Console",
    ) -> AgentRunTrace:
        """Provide human authorization and execute the safe simulation."""
        pass

    @abstractmethod
    def reject_run(
        self,
        run_id: str,
        recommendation_id: str,
        rejector: str = "ExecutiveOperationsVP",
        reason: str = "Rejected during executive review",
    ) -> AgentRunTrace:
        """Reject the proposed recommendation and block all action execution."""
        pass

    @abstractmethod
    def get_run_trace(self, run_id: str) -> Optional[AgentRunTrace]:
        """Retrieve the current state of an agent run trace."""
        pass
