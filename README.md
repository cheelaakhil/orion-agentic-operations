# ORION — AI Business Operations Intelligence System

> Detect. Investigate. Recommend. Act — with human oversight.

ORION is an AI-powered business operations intelligence system that detects
important business anomalies, investigates their root causes using specialized
agents, estimates business impact, recommends actions, and requires human
approval before consequential actions are executed.

---

## Overview

ORION monitors business operations data and autonomously:

1. **Detects** statistically significant anomalies in business metrics
2. **Investigates** root causes through a pipeline of specialized agents
3. **Estimates** business impact with deterministic calculations
4. **Recommends** corrective actions ranked by impact and feasibility
5. **Requests** human approval before executing consequential actions
6. **Executes** approved actions and logs a full audit trail

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ORION Frontend                          │
│               (Next.js / TypeScript / Tailwind)             │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                     ORION Backend                           │
│                  (Python / FastAPI)                         │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Data Layer  │  │ Analytics    │  │ Agent Orchestrator│  │
│  │ (SQL/ORM)   │  │ (Deterministic│  │ (Provider-Agnostic│  │
│  │             │  │  Calculations)│  │  Interface)       │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬──────────┘  │
│         │                │                    │             │
│  ┌──────▼────────────────▼────────────────────▼──────────┐  │
│  │                  MCP Tool Server                      │  │
│  │          (Model Context Protocol layer)               │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     PostgreSQL                              │
│         (Business data, audit logs, agent state)            │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Principles

### 1. Data-First Agent Architecture
Agents **never invent numerical evidence**. All quantitative analysis is
performed by deterministic Python/SQL calculations first. Agents reason over
verified, structured results — they do not hallucinate data.

### 2. Clear Separation of Concerns
The system enforces a strict pipeline:

| Layer              | Responsibility                                  |
|--------------------|------------------------------------------------|
| Data Retrieval     | SQL queries, data access via ORM               |
| Deterministic Analytics | Statistical calculations, anomaly detection |
| Agent Reasoning    | Interpretation, hypothesis generation          |
| Recommendations    | Action proposals ranked by impact              |
| Human Approval     | Explicit approval before consequential actions |
| Action Execution   | Controlled execution of approved actions       |
| Audit Logging      | Immutable record of every decision and action  |

### 3. Provider-Agnostic Agent Interface
The agent orchestration layer is designed with a clean abstraction that will
integrate with [Adya](https://adya.ai) as the agentic/orchestration platform.
The current implementation uses a provider-agnostic interface so that:

- No vendor-specific APIs are hard-coded
- Agent interfaces are defined as abstract Python classes
- Any orchestration platform can be plugged in via adapter pattern
- Adya integration will be a configuration change, not a rewrite

### 4. MCP-Ready Tool Architecture
Business tools are structured to be exposed through the
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) so that
external AI systems can discover and invoke them in a standardized way.

## Adya Integration Plan

ORION is designed to integrate with **Adya** as the agentic orchestration
platform. The integration points are:

| Component              | Current State           | With Adya                          |
|------------------------|-------------------------|------------------------------------|
| Agent Orchestration    | Local abstract interface| Adya orchestration API             |
| Agent Execution        | Local Python agents     | Adya-managed agent runtime         |
| Tool Discovery         | MCP server (local)      | Adya MCP registry                  |
| Conversation Memory    | PostgreSQL              | Adya conversation/context layer    |
| Human-in-the-Loop      | Local approval API      | Adya approval workflows            |

**What is NOT built internally:**
- No internal LLM inference engine — Adya will manage model access
- No internal agent memory/context system — Adya will provide this
- No internal tool registry — Adya will discover tools via MCP

**What IS built internally:**
- Deterministic data analytics (Python/SQL)
- Business logic and domain-specific calculations
- MCP tool definitions and implementations
- Database schema and data access layer
- Frontend dashboard and approval UI
- Audit logging infrastructure

## Project Structure

```
orion-agentic-operations/
├── frontend/          # Next.js + TypeScript + Tailwind dashboard
├── backend/           # Python + FastAPI backend
│   ├── api/           # REST API routes
│   ├── core/          # Configuration, dependencies
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic request/response schemas
│   ├── services/      # Business logic and analytics
│   └── tests/         # Backend tests
├── agents/            # Agent interface definitions and implementations
│   ├── interfaces/    # Abstract agent interfaces
│   ├── implementations/ # Concrete agent implementations
│   └── orchestrator/  # Supervisor and pipeline coordination
├── database/          # Database migrations and seed data
│   ├── migrations/    # Alembic migrations
│   └── seeds/         # Synthetic dataset generation
├── mcp/               # MCP tool server definitions
│   ├── tools/         # Individual tool implementations
│   └── server/        # MCP server configuration
├── data/              # Synthetic datasets and data generation scripts
├── evaluation/        # Evaluation framework and test scenarios
├── docs/              # Project documentation
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── AGENTS.md
│   ├── GOVERNANCE.md
│   ├── MCP_TOOLS.md
│   └── EVALUATION.md
└── README.md
```

## Quick Start & Demonstration Guide

### Prerequisites
- Python 3.11+ (Python 3.12 recommended)
- Node.js 18+ or 20+

### 1. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Generate Synthetic Dataset (NovaCart)
```bash
python -m data.generate
```

### 3. Start Backend API
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Interactive API docs available at: `http://127.0.0.1:8000/docs`

### 4. Start Next.js Executive Dashboard
```bash
cd frontend
npm run start -- -p 3000   # Production server (or npm run dev)
```
Executive Dashboard available at: `http://localhost:3000` (Open **Agent Run (MCP)** tab)

### 5. Run Standalone CLI Agentic Demo (Milestone 6A)
```bash
python -m agents.orchestrator.demo_runner
```

### 6. Run Model Context Protocol (MCP) Server (Milestone 5)
```bash
python -m orion_mcp.server
```

### 7. Run Test Suite
```bash
python -m pytest backend/tests -v
```

---

## Adya Integration Status

> [!NOTE]
> **STATUS: ADAPTER-READY ONLY**
> ORION provides a clean, provider-agnostic abstraction interface (`agents.runtime.AgentRuntimeProvider`) with an implementation (`agents.runtime.adya_runtime.AdyaAgentRuntime`) ready to connect to the Adya platform once credentials and runtime specifications are provided. **Adya is not claimed to be live-connected in this release.**

---

## Governance & Safety Guarantees

1. **Deterministic Data Grounding**: All quantitative metrics originate from SQL queries on the NovaCart dataset (52,000+ orders). No numerical figures are hallucinated.
2. **Mandatory Human-in-the-Loop Gate**: Autonomous investigation strictly halts at `WAITING_FOR_APPROVAL`.
3. **Execution Denied on Unapproved Actions**: Consequential action attempts without a valid approval token return `EXECUTION_DENIED`.
4. **Sandboxed Domain Simulations**: Approved actions execute strictly in `SIMULATED ACTION` mode with rollback instructions and configuration parameters logged to the immutable `audit_events` table.

---

## Deployment Modes & Architecture

| Mode | Frontend | Backend API | Database | Target Use Case |
|---|---|---|---|---|
| **Local Development** | `localhost:3000` (Next.js dev/start) | `127.0.0.1:8000` (Uvicorn) | SQLite / Local Postgres | Local evaluation & development |
| **Public Demo** *(Current)* | **Vercel** (`*.vercel.app`) | **Render Web Service** (`*.onrender.com`) | Managed PostgreSQL (Render/Neon) | Interactive public web demonstration |
| **Production Enterprise** | Enterprise Edge / CDN | Dedicated Kubernetes / Cloud Run | HA Managed PostgreSQL Cluster | Live multi-tenant operational deployment |

For step-by-step public demo deployment instructions, refer to the [Deployment Runbook](docs/DEPLOYMENT.md), [Deployment Plan](docs/DEPLOYMENT_PLAN.md), and [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md).

---

## License

Proprietary — Internal use only.
