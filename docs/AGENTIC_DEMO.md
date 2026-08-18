# ORION — Milestone 6A: Agentic Demonstration & Orchestration

> [!NOTE]
> **MILESTONE 6A COMPLIANCE NOTICE**:
> This document details the **provider-agnostic Agentic Orchestration Layer** implemented on top of ORION's verified Model Context Protocol (MCP) tool layer.
> **Adya integration is not implemented in this milestone.** This implementation provides the provider abstraction (`AgentRuntimeProvider`) and verified `LocalAgentRuntime` to enable a seamless future connection to Adya once credentials and specs are provided.

---

## 1. System Architecture

The Agentic Demonstration layer acts as a workflow coordinator that consumes ORION's 18 MCP tools as its sole capability boundary.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT RUNTIME PROVIDER INTERFACE                         │
│                    (agents.runtime.AgentRuntimeProvider)                    │
│                                                                             │
│   ┌───────────────────────────────────┐ ┌───────────────────────────────┐   │
│   │ LocalAgentRuntime (Active in 6A)  │ │ AdyaAgentRuntime (Future 6B)  │   │
│   └─────────────────┬─────────────────┘ └───────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────────────────┘
                      │ Tool Calls over MCP Boundary
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ORION MCP TOOL LAYER (18 Tools)                       │
│                                                                             │
│   [READ_ONLY]    get_business_anomalies, get_anomaly_evidence, etc.         │
│   [ANALYSIS]     start_investigation, calculate_business_impact             │
│   [PROPOSAL]     get_recommendations, request_approval                      │
│   [APPROVAL]     approve_recommendation, reject_recommendation              │
│   [ACTION]       execute_approved_action (Token-gated simulation)           │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │ Deterministic Database Invocations
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ORION DETERMINISTIC CORE ENGINE                       │
│   - Multi-agent causal pipeline (Data, Anomaly, Root, Impact, Rec, Action)  │
│   - NovaCart Dataset (52,000+ orders, 5,000 customers, 200 products)        │
│   - Immutable Operations Audit Trail (audit_events)                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Logical Agent Roles & Responsibilities

| Agent Role | Primary Responsibility | MCP Tool Bound | Output / Evidence Type |
|---|---|---|---|
| **Supervisor Agent** | Discovers active anomalies across the enterprise dataset and selects the critical investigation target. | `get_business_anomalies` | `OBSERVED` |
| **Data Analyst Agent** | Extracts multi-dimensional quantitative baseline vs evaluation evidence packages. | `get_anomaly_evidence` | `OBSERVED` |
| **Investigation Agent** | Dispatches causal fact classification and temporal onset isolation. | `start_investigation` | `INFERRED` |
| **Root Cause Agent** | Ranks causal hypotheses based on empirical evidence support. | `get_investigation` | `HYPOTHESIS` |
| **Business Impact Agent**| Computes realized revenue loss and 30-day/90-day forward financial risk. | `calculate_business_impact` | `OBSERVED` |
| **Recommendation Agent**| Formulates prioritized, actionable operational remediations with projected ROI. | `get_recommendations` | `PROPOSAL` |
| **Governance Agent** | Creates pending authorization requests and halts pipeline at Human Approval Gate. | `request_approval` | `PROPOSAL` |
| **Human Executive** | Authorizes (`approve_recommendation`) or blocks (`reject_recommendation`) actions. | `approve_recommendation` / `reject_recommendation` | `ACTION_RESULT` |
| **Action Agent** | Executes safe operational simulations using approved authorization tokens. | `execute_approved_action` | `ACTION_RESULT` (`SIMULATED ACTION`) |
| **Audit Agent** | Confirms all state transitions, approvals, and executions in immutable audit log. | `get_audit_events` | `OBSERVED` |

---

## 3. The 13-Step Deterministic Workflow (`ANOM-REV-001`)

1. **Anomaly Detection**: Supervisor agent invokes `get_business_anomalies()` → Discovers critical revenue anomaly `ANOM-REV-001` (-43.0% daily revenue decline).
2. **Target Selection**: Targets `ANOM-REV-001` ($163,189.54 vs $286,343.91 baseline).
3. **Evidence Extraction**: Data Analyst calls `get_anomaly_evidence('ANOM-REV-001')` → Identifies 86.7% support SLA breach rate and 19.8% Electronics stockout rate.
4. **Investigation Dispatch**: Investigation Agent calls `start_investigation('ANOM-REV-001')` → Generates `INV-XXXX` with 88% confidence.
5. **Findings Retrieval**: Root cause agent queries `get_investigation()` → Identifies support bottleneck as primary driver of repeat customer churn.
6. **Root Cause Isolation**: Confirms temporal onset: Support SLA spikes preceded revenue decline.
7. **Business Impact Calculation**: Business impact agent calls `calculate_business_impact('ANOM-REV-001')` → Computes realized loss of **$7,300,045.62** and 30-day risk of **$5,093,055.00** across 813 accounts.
8. **Recommendation Generation**: Recommendation agent calls `get_recommendations()` → Generates 4 ranked interventions (`REC-001` to `REC-004`).
9. **Approval Request**: Governance agent calls `request_approval('REC-001')` → Registers `APPR-REC-001` with status `PENDING_APPROVAL`.
10. **Human Approval Gate (Execution Paused)**: Workflow pauses. No action agent can execute without human sign-off.
11. **Human Executive Decision**:
    - **Approve**: Issues valid execution token `APPR-REC-001` (Status: `APPROVED`).
    - **Reject**: Permanently marks status `REJECTED`, blocking execution with `EXECUTION_DENIED`.
12. **Safe Action Simulation**: Action agent calls `execute_approved_action('ACT-REC-001', 'APPR-REC-001')` → Applies simulated support staffing reallocation (+15 Tier-1/Tier-2 specialists, throughput 42 → 128 tickets/hr) labeled `SIMULATED ACTION`.
13. **Audit Verification**: Audit agent calls `get_audit_events()` to confirm end-to-end trace persistence.

---

## 4. Evidence Classification Model

ORION enforces strict distinction between observed facts, analytical inferences, and working hypotheses:

* **`[OBSERVED]`**: Deterministic figures directly calculated from SQL database tables (e.g. `Revenue declined 43.0%`, Source: `get_business_anomalies`).
* **`[INFERRED]`**: Analytical conclusions produced by multi-agent causal correlation (e.g. `Support bottleneck caused repeat customer cancellation spike`, Source: `start_investigation`).
* **`[HYPOTHESIS]`**: Ranked candidate root-cause theories awaiting empirical validation (e.g. `Hypothesis 1: Customer support SLA breach surge`, Source: `get_investigation`).
* **`[PROPOSAL]`**: Candidate operational interventions formulated by recommendation agents (e.g. `REC-001: Support Team Capacity Escalation`, Source: `get_recommendations`).
* **`[ACTION_RESULT]`**: Verified outcomes from safe simulation execution (e.g. `15 support specialists reallocated in simulation`, Source: `execute_approved_action`).

---

## 5. Provider Abstraction Architecture

Located at [`agents/runtime/provider.py`](file:///c:/Users/akhil/ORION/orion-agentic-operations/agents/runtime/provider.py):

```python
class AgentRuntimeProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str: ...
    
    @abstractmethod
    def discover_tools(self) -> Dict[str, str]: ...
    
    @abstractmethod
    def start_agent_run(self, anomaly_id: str) -> AgentRunTrace: ...
    
    @abstractmethod
    def approve_and_execute(self, run_id: str, recommendation_id: str, approver: str, reason: str) -> AgentRunTrace: ...
    
    @abstractmethod
    def reject_run(self, run_id: str, recommendation_id: str, rejector: str, reason: str) -> AgentRunTrace: ...
    
    @abstractmethod
    def get_run_trace(self, run_id: str) -> Optional[AgentRunTrace]: ...
```

### Local Implementation (`LocalAgentRuntime`)
* Ships in Milestone 6A as [`agents/runtime/local_runtime.py`](file:///c:/Users/akhil/ORION/orion-agentic-operations/agents/runtime/local_runtime.py).
* Fully deterministic, reproducible, and zero-cost (no external LLM API billing).

### Future Adya Integration Point (`AdyaAgentRuntime`)
* Will implement `AgentRuntimeProvider` by translating Adya runtime callbacks to ORION MCP tools.
* Will preserve all ORION safety classifications, human approval gates, and deterministic data grounding.

---

## 6. How to Run the Demonstration

### CLI Runner
```bash
python -m agents.orchestrator.demo_runner
```

### Executive Web Dashboard
1. Ensure backend is running: `uvicorn backend.main:app --port 8000`
2. Ensure frontend is running: `npm run dev` in `frontend/`
3. Navigate to `http://localhost:3000` and click on **Agent Run (MCP)** in the sidebar.
4. Review the interactive workflow pipeline, agent trace, and approve the simulation!
