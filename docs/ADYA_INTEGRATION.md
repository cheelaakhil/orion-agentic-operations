# ORION — Adya Integration Architecture & MCP Interface Guide

> [!NOTE]
> This document outlines the architectural interface through which an external agent runtime, such as **Adya**, connects to ORION via the Model Context Protocol (MCP).
> All integration points described herein are **proposed interface mappings** based on standard MCP protocols, rather than confirmed or proprietary Adya APIs.

---

## 1. What ORION Exposes Through MCP

ORION exposes 18 standardized operational tools organized into 5 functional categories:

1. **Deterministic Business Analytics (Read-Only)**: SQL-grounded querying of revenue, orders, support tickets, inventory snapshots, customer segments, and marketing channels.
2. **Autonomous Multi-Agent Investigations (Analysis)**: Causal reasoning, temporal onset detection (June 20, 2026), cross-dimensional correlation, and deterministic loss modeling ($7.30M realized loss).
3. **Remediation Proposals (Proposal)**: Prioritized recovery recommendations with expected revenue impacts.
4. **Human-in-the-Loop Governance (Approval)**: Explicit human authorization and rejection state machine (`PROPOSED` → `PENDING_APPROVAL` → `APPROVED` / `REJECTED`).
5. **Controlled Operational Simulations (Consequential Action)**: Safe domain execution simulations with complete immutable audit tracking.

---

## 2. Why the MCP Layer is Provider-Agnostic

ORION follows a strict separation of concerns:
- **Core Intelligence & Analytics Layer**: Implemented in Python / SQLAlchemy with deterministic SQL calculations.
- **Agent Protocol Layer**: Uses standard MCP (Model Context Protocol) JSON-RPC interfaces.
- **Independence**: ORION requires **zero** vendor-specific agent libraries or proprietary runtime bindings. Any MCP-compatible client (Adya, Claude Desktop, Cursor, LangChain, or custom autonomous agents) can discover and invoke ORION tools natively.

---

## 3. Connection Topologies

```
┌─────────────────────────────────────────────────────────────┐
│             External Agent Runtime (e.g. Adya)              │
│                                                             │
│  - Receives business goal: "Investigate revenue decline"     │
│  - Discovers tools via MCP ListTools request                │
│  - Executes multi-step plan through tool invocations        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                Standard MCP Transport (JSON-RPC)
                - stdio (local subprocess)
                - SSE / HTTP (remote container service)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    ORION MCP Server                         │
│                    (mcp/server.py)                          │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Authorization & Safety Guardrails                   │   │
│   │ - Enforces human approval tokens for actions         │   │
│   │ - Blocks LLMs from mutating database directly        │   │
│   │ - Enforces safe simulation mode                     │   │
│   └──────────────────────────┬──────────────────────────┘   │
└──────────────────────────────┼──────────────────────────────┘
                               │ Python Service Calls
┌──────────────────────────────▼──────────────────────────────┐
│      ORION Deterministic Services & Local Agents            │
│      - AnomalyEngine, EvidenceBuilder, Supervisor           │
│      - SQLite / PostgreSQL Database (NovaCart Dataset)      │
│      - Immutable Audit Trail (audit_events)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Tool Categorization & Safety Matrix

### A. Read-Only Tools (No Side Effects)
- `get_business_anomalies`
- `get_anomaly_evidence`
- `get_revenue_analytics`
- `get_revenue_by_region`
- `get_revenue_by_product`
- `get_customer_analytics`
- `get_support_analytics`
- `get_inventory_analytics`
- `get_marketing_analytics`
- `get_investigation`
- `get_audit_events`

### B. Analytical Synthesis Tools (Compute Only)
- `start_investigation`
- `calculate_business_impact`

### C. Proposal & Governance Tools
- `get_recommendations`
- `request_approval`

### D. Tools Requiring Human Approval (State Mutating)
- `approve_recommendation` *(Requires authorized human operator)*
- `reject_recommendation` *(Requires authorized human operator)*

### E. Consequential Action Tools (Controlled Execution)
- `execute_approved_action`
  - **Prerequisite**: Valid `approval_id` with `status: "APPROVED"`.
  - **Safety**: Safe domain simulation (`SIMULATED ACTION`).

---

## 5. Configuration for Future Adya Runtime Deployment

When Adya credentials, SDKs, or cloud endpoints become available, the following configuration steps would integrate ORION into an Adya deployment:

### 1. Register ORION MCP Server in Adya Configuration
*(Proposed JSON configuration structure)*:
```json
{
  "mcpServers": {
    "orion": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/orion-agentic-operations",
      "env": {
        "ORION_DATABASE_URL": "postgresql://orion:orion@postgres:5432/orion",
        "ORION_AGENT_PROVIDER": "local"
      }
    }
  }
}
```

### 2. Configure Human-in-the-Loop Webhooks
When Adya triggers `request_approval`, Adya's human-in-the-loop workflow can notify executive stakeholders via Slack, Teams, or the ORION Executive Operations Dashboard.

### 3. Maintain Audit Traceability
All Adya agent tool invocations automatically carry the actor name (`mcp_action_agent` or Adya Agent ID) into ORION's `audit_events` table for compliance and post-incident review.
