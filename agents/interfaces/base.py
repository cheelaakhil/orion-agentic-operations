"""
Base Agent Interface for ORION.

All agents implement this abstract interface. The interface is
provider-agnostic — implementations can run locally or through
an external orchestrator like Adya.

Key design principle: Agents receive pre-computed, verified data
and produce structured reasoning output. They NEVER generate
numerical evidence — all numbers come from deterministic
Python/SQL calculations upstream.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Type

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AgentStatus(str, Enum):
    """Status of an agent execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class Severity(str, Enum):
    """Severity classification for anomalies and impacts."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Common Schemas
# ---------------------------------------------------------------------------

class TimeRange(BaseModel):
    """A time period for analysis."""
    start_date: str = Field(..., description="ISO date string YYYY-MM-DD")
    end_date: str = Field(..., description="ISO date string YYYY-MM-DD")


class EvidenceItem(BaseModel):
    """A single piece of evidence supporting a finding."""
    source_dimension: str = Field(..., description="e.g. 'revenue', 'support'")
    metric: str = Field(..., description="Specific metric name")
    observation: str = Field(..., description="Human-readable observation")
    data_reference: str = Field(..., description="Reference to source query/result ID")
    value: Any = Field(default=None, description="The actual data value")


class AnomalyRecord(BaseModel):
    """A detected anomaly passed to agents for investigation."""
    anomaly_id: str
    metric_name: str
    metric_value: float
    expected_value: float
    deviation_pct: float
    severity: Severity
    detected_at: str
    onset_date: str | None = None
    description: str | None = None


class AgentMessage(BaseModel):
    """Structured message passed between agents via Supervisor."""
    source_agent: str
    target_agent: str
    investigation_id: str
    message_type: str = Field(..., description="input | output | error | status")
    payload: dict[str, Any]
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    trace_id: str = Field(..., description="Correlation ID for audit trail")


class AgentExecutionResult(BaseModel):
    """Wrapper for agent execution output with metadata."""
    agent_name: str
    status: AgentStatus
    started_at: str
    completed_at: str | None = None
    duration_ms: int | None = None
    output: dict[str, Any] | None = None
    error: str | None = None
    trace_id: str


# ---------------------------------------------------------------------------
# Base Agent Interface
# ---------------------------------------------------------------------------

class BaseAgent(ABC):
    """
    Abstract base class for all ORION agents.

    Every agent must define:
    - What data it accepts (input_schema)
    - What it produces (output_schema)
    - Which MCP tools it may invoke (tools)
    - How it executes (execute method)
    - How to validate its output (validate_output method)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier (e.g. 'data_analysis_agent')."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this agent does."""

    @property
    @abstractmethod
    def input_schema(self) -> Type[BaseModel]:
        """Pydantic model class defining the agent's required input."""

    @property
    @abstractmethod
    def output_schema(self) -> Type[BaseModel]:
        """Pydantic model class defining the agent's structured output."""

    @property
    @abstractmethod
    def tools(self) -> list[str]:
        """List of MCP tool names this agent is allowed to invoke."""

    @abstractmethod
    async def execute(self, input_data: BaseModel) -> BaseModel:
        """
        Execute the agent's task.

        Args:
            input_data: Validated input matching self.input_schema.

        Returns:
            Structured output matching self.output_schema.

        Raises:
            AgentExecutionError: If execution fails.
        """

    @abstractmethod
    async def validate_output(self, output: BaseModel) -> bool:
        """
        Validate that the agent's output meets quality criteria.

        Args:
            output: The agent's output to validate.

        Returns:
            True if output is valid, False otherwise.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"


# ---------------------------------------------------------------------------
# Provider Adapter Interface
# ---------------------------------------------------------------------------

class AgentProvider(ABC):
    """
    Abstract interface for agent execution providers.

    Implementations:
    - LocalProvider: Runs agents in-process (development/testing)
    - AdyaProvider: Delegates to Adya orchestration API (future)
    """

    @abstractmethod
    async def execute_agent(
        self,
        agent_name: str,
        input_data: dict[str, Any],
        tools: list[str],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an agent through this provider.

        Args:
            agent_name: Name of the agent to execute.
            input_data: Input data for the agent.
            tools: List of MCP tool names the agent may use.
            context: Optional execution context (investigation ID, etc.).

        Returns:
            Agent output as a dictionary.
        """

    @abstractmethod
    async def get_agent_status(self, execution_id: str) -> AgentStatus:
        """Check the current status of an agent execution."""


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AgentExecutionError(Exception):
    """Raised when an agent execution fails."""

    def __init__(self, agent_name: str, message: str, details: dict | None = None):
        self.agent_name = agent_name
        self.details = details or {}
        super().__init__(f"Agent '{agent_name}' failed: {message}")


class AgentValidationError(Exception):
    """Raised when agent output fails validation."""

    def __init__(self, agent_name: str, violations: list[str]):
        self.agent_name = agent_name
        self.violations = violations
        super().__init__(
            f"Agent '{agent_name}' output validation failed: {violations}"
        )
