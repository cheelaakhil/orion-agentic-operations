# ORION — Milestone 6 Integration Plan: External Agent Runtime & Adya Connection

> [!IMPORTANT]
> **PLANNING DOCUMENT ONLY**: This document specifies the integration architecture and engineering roadmap for connecting ORION to **Adya's** agentic runtime once official credentials, endpoints, and protocol specifications are provided.
> No Milestone 6 implementation has been started. All interface bindings herein represent proposed architectural integration points.

---

## 1. Executive Summary & Objective

In Milestones 1 through 5, ORION established:
1. Deterministic database analytics over the NovaCart dataset (52,000+ orders).
2. Autonomous multi-agent causal investigation pipeline with 100% data grounding.
3. Executive command center dashboard built with Next.js and Tailwind.
4. Production-ready Model Context Protocol (MCP) server exposing 18 business tools across 5 safety tiers.

The objective of **Milestone 6** is to connect an external autonomous runtime (specifically **Adya**) to ORION's verified MCP server, enabling Adya agents to autonomously query data, orchestrate investigations, request human authorizations, and execute safe operational simulations.

---

## 2. System Topology & Architectural Boundary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             ADYA AGENT RUNTIME                              │
│                                                                             │
│   ┌───────────────────────┐              ┌──────────────────────────────┐   │
│   │ Adya Executive Agent  │              │ Adya Working Memory / State  │   │
│   │ (Goal: Resolve Anoms) │              │ (Context, Session History)   │   │
│   └───────────┬───────────┘              └──────────────┬───────────────┘   │
└───────────────┼─────────────────────────────────────────┼───────────────────┘
                │                                         │
                │ JSON-RPC over stdio / SSE               │
                ▼                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORION MCP SERVER LAYER                             │
│                          (orion_mcp/server.py)                              │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Tool Safety Classification & Authorization Firewall                 │   │
│   │ - READ_ONLY: Query without mutation                                │   │
│   │ - ANALYSIS: Multi-agent compute                                     │   │
│   │ - PROPOSAL: Generate ranked recommendations                         │   │
│   │ - APPROVAL: Human operator authorization                            │   │
│   │ - CONSEQUENTIAL_ACTION: Token-gated simulation execution            │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │ Python Service Invocations
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    ORION DETERMINISTIC CORE ENGINE                          │
│                                                                             │
│   ┌──────────────────────────┐             ┌────────────────────────────┐   │
│   │ Supervisor Orchestrator  │             │ Deterministic Analytics    │   │
│   │ (Data, Anomaly, Root,    │             │ (Revenue, Support, Inv,    │   │
│   │  Impact, Rec, Action)    │             │  Customers, Marketing)     │   │
│   └────────────┬─────────────┘             └─────────────┬──────────────┘   │
│                │                                         │                  │
│   ┌────────────▼─────────────────────────────────────────▼──────────────┐   │
│   │ SQLite / PostgreSQL Production Database (NovaCart Dataset)          │   │
│   │ Immutable Operations Audit Trail (audit_events)                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Integration Components

### 3.1 Tool Discovery
* **Mechanism**: Standard MCP `tools/list` protocol request.
* **Payload**: Adya discovers all 18 registered ORION tools with structured JSON schemas, parameter requirements, and descriptions.
* **Assumption**: *Adya supports standard MCP (Model Context Protocol) 2024-11-05 spec or higher.*

### 3.2 Autonomous Goal Formulation & Multi-Agent Investigation
1. Adya receives top-level operations objective: `"Identify and resolve root causes of recent business metric anomalies."`
2. Adya calls `get_business_anomalies(severity='CRITICAL')` → discovers `ANOM-REV-001` (-43.0% daily revenue drop) and `ANOM-SUP-001` (86.7% SLA breach rate).
3. Adya calls `get_anomaly_evidence('ANOM-REV-001')` → receives quantitative evidence package across dimensions.
4. Adya calls `calculate_business_impact('ANOM-REV-001')` → receives grounded financial loss calculation ($7.30M realized loss).
5. Adya calls `start_investigation('ANOM-REV-001')` → invokes ORION's 5-agent pipeline producing ranked hypotheses and prioritized recommendations (`REC-001` to `REC-004`).

### 3.3 Governance Boundary & Human Approval Flow
* **Safety Rule**: Adya **CANNOT** execute operational actions unilaterally.
* **Flow**:
  1. Adya calls `get_recommendations(investigation_id)` to review candidate remediations.
  2. Adya calls `request_approval(recommendation_id='REC-001')` → creates `PENDING_APPROVAL` authorization record in ORION.
  3. Adya surfaces an interactive approval card to the human executive in the ORION Command Center or via webhook notification.
  4. Human operator reviews evidence and executes `approve_recommendation('REC-001')` → issues authorization token `APPR-REC-001`.
  5. Adya passes authorization token to `execute_approved_action(action_id='ACT-REC-001', approval_id='APPR-REC-001')`.

### 3.4 Action Simulation & Audit Traceability
* Action agent simulates operational adjustments:
  - Simulated support staffing capacity reallocation (+15 Tier-1/Tier-2 specialists).
  - Simulated automated triage macros for delivery status.
  - Simulated throughput scaling (42 → 128 tickets/hr).
* Result is recorded in `action_executions` with label `SIMULATED ACTION`.
* Complete transaction lifecycle is committed to `audit_events` with actor tag `adya_agent_runtime`.

---

## 4. Memory & Context Considerations

| Consideration | Engineering Strategy |
|---|---|
| **Context Window Optimization** | Instead of passing raw 52,000 order rows, ORION's MCP tools return pre-aggregated, deterministic evidence packages. |
| **State Persistence** | Investigation state, tokens, and audit events are stored in ORION's relational database, keeping Adya stateless across sessions. |
| **Idempotency** | Action execution tokens (`APPR-REC-XXX`) expire immediately upon execution to prevent duplicate or looping tool calls. |

---

## 5. Deployment Architecture

### Mode A: Local Subprocess (stdio Transport)
* Adya runtime spawns `python -m orion_mcp.server` as a child process via `stdin`/`stdout`.
* Ideal for local development, CLI agents, and developer workstations.

### Mode B: Remote Containerized Service (SSE Transport)
* ORION MCP Server deployed as an HTTP/SSE service on port `8001` alongside FastAPI backend on port `8000`.
* Adya connects via Server-Sent Events (SSE) endpoint: `http://orion-backend:8001/sse`.
* Secured via mutual TLS or bearer API token authentication.

---

## 6. Assumptions & Prerequisites for Milestone 6 Execution

1. **Adya Connection Parameters**: Official Adya runtime documentation, environment variables, or webhook protocol URLs must be provided.
2. **Deterministic Source of Truth**: The ORION backend database remains the sole authority on financial metrics; Adya will not overwrite SQL calculations.
3. **Human Authorization**: Human executive sign-off remains mandatory for all consequential operational remediations.
