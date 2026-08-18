# ORION — Agent Specifications

## 1. Agent Design Principles

### Data-First Architecture
Every agent in ORION operates under a strict principle:

> **Agents reason over structured, verified data. They never invent
> numerical evidence.**

This means:
- All quantitative analysis is performed by deterministic Python/SQL first
- Agents receive pre-computed results as structured input
- Agent output is interpretation, reasoning, and recommendations
- Every data point in agent output is traceable to a source query

### Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: DATA RETRIEVAL          (SQL / ORM)            │
│   → Raw data fetched from PostgreSQL                    │
├─────────────────────────────────────────────────────────┤
│ Layer 2: DETERMINISTIC ANALYTICS (Python)               │
│   → Statistical calculations, aggregations, scoring    │
├─────────────────────────────────────────────────────────┤
│ Layer 3: AGENT REASONING         (LLM via Adya)        │
│   → Interpretation, hypothesis generation, narrative   │
├─────────────────────────────────────────────────────────┤
│ Layer 4: RECOMMENDATIONS         (Agent + Rules)       │
│   → Prioritized actions with expected impact           │
├─────────────────────────────────────────────────────────┤
│ Layer 5: HUMAN APPROVAL          (Dashboard UI)        │
│   → Human reviews evidence and approves/rejects        │
├─────────────────────────────────────────────────────────┤
│ Layer 6: ACTION EXECUTION        (Action Handlers)     │
│   → Approved actions executed with status tracking     │
├─────────────────────────────────────────────────────────┤
│ Layer 7: AUDIT LOGGING           (Immutable Log)       │
│   → Every step recorded with timestamp and actor       │
└─────────────────────────────────────────────────────────┘
```

## 2. Agent Interface Contract

Every agent implements the following abstract interface:

```python
class BaseAgent(ABC):
    """Base interface for all ORION agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of agent purpose."""

    @property
    @abstractmethod
    def input_schema(self) -> Type[BaseModel]:
        """Pydantic model defining required input."""

    @property
    @abstractmethod
    def output_schema(self) -> Type[BaseModel]:
        """Pydantic model defining structured output."""

    @property
    @abstractmethod
    def tools(self) -> list[str]:
        """List of MCP tool names this agent may invoke."""

    @abstractmethod
    async def execute(self, input_data: BaseModel) -> BaseModel:
        """Execute the agent's task and return structured output."""

    @abstractmethod
    async def validate_output(self, output: BaseModel) -> bool:
        """Validate that output meets quality and completeness criteria."""
```

## 3. Agent Specifications

### 3.1 SupervisorAgent

**Purpose**: Orchestrates the investigation pipeline. Decides which agents
to invoke, in what order, and how to merge their outputs into a coherent
investigation report.

**NOT an LLM agent in v1**: The Supervisor is implemented as a deterministic
state machine in v1. It becomes an LLM-driven orchestrator when Adya is
integrated.

```
Input:
  - anomaly_id: str
  - anomaly_details: AnomalyRecord
  - investigation_config: InvestigationConfig (optional overrides)

Output:
  - investigation_id: str
  - status: InvestigationStatus
  - timeline: list[InvestigationStep]
  - root_causes: list[RootCauseHypothesis]
  - confidence_score: float (0.0–1.0)
  - business_impact: BusinessImpactReport
  - recommendations: list[Recommendation]
  - requires_approval: bool

Pipeline Order:
  1. DataAnalysisAgent  → gathers and structures data
  2. AnomalyInvestigationAgent → pattern analysis
  3. RootCauseAgent → hypothesis generation
  4. BusinessImpactAgent → impact quantification
  5. RecommendationAgent → action proposals
  6. [Human Approval]
  7. ActionAgent → execute approved actions

Tools: None (orchestration only)
```

### 3.2 DataAnalysisAgent

**Purpose**: Retrieves and structures business data across all investigation
dimensions. Performs deterministic calculations and produces structured
analytical summaries.

**Key constraint**: This agent performs SQL queries and statistical
calculations. It does NOT use LLM for any numerical computation.

```
Input:
  - investigation_id: str
  - anomaly: AnomalyRecord
  - dimensions: list[str]  # e.g., ["revenue", "support", "inventory"]
  - time_range: TimeRange

Output:
  - dimension_analyses: dict[str, DimensionAnalysis]
    Each DimensionAnalysis contains:
      - metric_summaries: list[MetricSummary]
      - trends: list[TrendAnalysis]
      - statistical_tests: list[StatisticalTest]
      - notable_changes: list[NotableChange]
  - cross_dimension_correlations: list[Correlation]
  - data_quality_report: DataQualityReport

Tools:
  - query_revenue_metrics
  - query_customer_metrics
  - query_support_metrics
  - query_inventory_metrics
  - query_marketing_metrics
  - compute_statistical_tests
```

### 3.3 AnomalyInvestigationAgent

**Purpose**: Analyzes anomaly patterns across the structured data produced
by DataAnalysisAgent. Identifies temporal patterns, correlations, and
anomaly propagation paths.

**What this agent DOES**: Interprets pre-computed statistical results to
identify patterns a human analyst would look for.

**What this agent DOES NOT do**: Compute statistics, generate numbers, or
perform calculations.

```
Input:
  - investigation_id: str
  - anomaly: AnomalyRecord
  - dimension_analyses: dict[str, DimensionAnalysis]
  - correlations: list[Correlation]

Output:
  - pattern_analysis: PatternAnalysis
    - temporal_patterns: list[TemporalPattern]
    - correlation_narratives: list[CorrelationNarrative]
    - propagation_path: list[PropagationStep]
  - anomaly_classification: AnomalyClassification
    - type: str  # "systemic", "localized", "seasonal", "external"
    - affected_dimensions: list[str]
    - onset_analysis: OnsetAnalysis
  - key_findings: list[Finding]

Tools:
  - query_revenue_metrics
  - query_support_metrics
  - query_inventory_metrics
  - compute_correlation
```

### 3.4 RootCauseAgent

**Purpose**: Generates ranked root-cause hypotheses based on the evidence
gathered by previous agents. Each hypothesis must cite specific data points.

**Critical rule**: Confidence scores are derived from statistical evidence
strength, not from LLM self-assessment.

```
Input:
  - investigation_id: str
  - anomaly: AnomalyRecord
  - dimension_analyses: dict[str, DimensionAnalysis]
  - pattern_analysis: PatternAnalysis
  - anomaly_classification: AnomalyClassification

Output:
  - hypotheses: list[RootCauseHypothesis]
    Each hypothesis contains:
      - hypothesis_id: str
      - description: str
      - confidence: float (0.0–1.0, computed from evidence)
      - evidence: list[EvidenceItem]
        Each evidence item:
          - source_dimension: str
          - metric: str
          - observation: str
          - data_reference: str  # links to specific query result
      - causal_chain: list[CausalStep]
      - alternative_explanations: list[str]
  - primary_root_cause: str  # hypothesis_id of highest confidence
  - evidence_strength: EvidenceStrengthReport

Tools:
  - query_revenue_metrics
  - query_support_metrics
  - query_customer_metrics
  - compute_correlation
  - compute_statistical_tests
```

### 3.5 BusinessImpactAgent

**Purpose**: Quantifies the business impact of the identified root causes.
All financial calculations are deterministic — the agent adds narrative
context and projections.

```
Input:
  - investigation_id: str
  - anomaly: AnomalyRecord
  - root_causes: list[RootCauseHypothesis]
  - dimension_analyses: dict[str, DimensionAnalysis]

Output:
  - realized_impact: RealizedImpact
    - revenue_loss: float  # computed by SQL
    - customer_churn_count: int  # computed by SQL
    - support_cost_increase: float  # computed by SQL
    - period: TimeRange
  - projected_impact: ProjectedImpact
    - revenue_at_risk_30d: float  # deterministic projection
    - revenue_at_risk_90d: float
    - customers_at_risk: int
    - methodology: str  # description of projection method
  - impact_by_dimension: dict[str, DimensionImpact]
  - severity_assessment: SeverityAssessment
    - level: str  # "critical", "high", "medium", "low"
    - justification: str
  - narrative_summary: str  # Agent-generated narrative

Tools:
  - query_revenue_metrics
  - query_customer_metrics
  - compute_revenue_projection
  - compute_churn_projection
```

### 3.6 RecommendationAgent

**Purpose**: Generates prioritized action recommendations based on root
causes and business impact. Each recommendation includes expected impact,
implementation difficulty, and time-to-effect.

```
Input:
  - investigation_id: str
  - root_causes: list[RootCauseHypothesis]
  - business_impact: BusinessImpactReport
  - current_metrics: dict[str, MetricSummary]

Output:
  - recommendations: list[Recommendation]
    Each recommendation:
      - recommendation_id: str
      - title: str
      - description: str
      - category: str  # "immediate", "short_term", "long_term"
      - priority: int  # 1 = highest
      - expected_impact: ExpectedImpact
        - metric: str
        - estimated_improvement: float
        - confidence: float
        - time_to_effect: str
      - implementation: ImplementationDetails
        - difficulty: str  # "low", "medium", "high"
        - estimated_cost: float (optional)
        - prerequisites: list[str]
      - risks: list[str]
      - addresses_root_cause: str  # hypothesis_id
      - requires_approval: bool
      - action_type: str  # maps to ActionAgent capability

Tools:
  - query_revenue_metrics
  - query_support_metrics
  - query_inventory_metrics
```

### 3.7 ActionAgent

**Purpose**: Executes approved actions. Each action type has a registered
handler. The ActionAgent validates preconditions, executes the action,
and reports results.

**Critical rule**: ActionAgent ONLY executes actions that have been
explicitly approved by a human through the approval workflow.

```
Input:
  - action_id: str
  - action_type: str
  - parameters: dict
  - approval_id: str  # must reference a valid approval

Output:
  - execution_id: str
  - status: str  # "success", "partial", "failed", "rolled_back"
  - result: ActionResult
    - changes_made: list[str]
    - metrics_affected: list[str]
    - rollback_available: bool
  - error: str (optional)
  - audit_entry: AuditLogEntry

Action Types (v1):
  - adjust_support_staffing: Simulated staffing change
  - trigger_inventory_reorder: Simulated reorder
  - adjust_marketing_budget: Simulated budget reallocation
  - create_customer_retention_campaign: Simulated campaign
  - escalate_to_management: Creates escalation notification

Tools:
  - execute_support_action
  - execute_inventory_action
  - execute_marketing_action
  - log_audit_entry
```

## 4. Agent Communication Protocol

Agents communicate through the SupervisorAgent using structured messages:

```python
@dataclass
class AgentMessage:
    """Structured message passed between agents via Supervisor."""
    source_agent: str
    target_agent: str
    investigation_id: str
    message_type: str  # "input", "output", "error", "status"
    payload: dict
    timestamp: datetime
    trace_id: str  # for audit trail correlation
```

## 5. Provider Adapter Interface

When Adya is integrated, a provider adapter translates between ORION's
agent interface and Adya's orchestration API:

```python
class AgentProvider(ABC):
    """Abstract interface for agent execution providers."""

    @abstractmethod
    async def execute_agent(
        self,
        agent_name: str,
        input_data: dict,
        tools: list[str],
        context: dict
    ) -> dict:
        """Execute an agent through the provider."""

    @abstractmethod
    async def get_agent_status(self, execution_id: str) -> str:
        """Check agent execution status."""

class LocalProvider(AgentProvider):
    """Local execution provider for development/testing."""

class AdyaProvider(AgentProvider):
    """Adya execution provider (future integration)."""
```

## 6. Error Handling

Each agent must handle:
- **Data unavailability**: Return partial results with data quality flags
- **Timeout**: Return best-effort results within time budget
- **Upstream failure**: Handle missing input from previous agents gracefully
- **Validation failure**: Report output validation errors to Supervisor
