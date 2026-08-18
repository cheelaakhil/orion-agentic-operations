# ORION — Public Demonstration Deployment Plan

> Architecture, strategy, and readiness plan for deploying ORION to Vercel (Frontend), Render (FastAPI Backend), and Managed PostgreSQL.

---

## 1. Executive Summary

This document outlines the deployment strategy for ORION for a public demonstration environment. The target architecture separates the Next.js Executive Operations Dashboard (hosted on Vercel) from the Python/FastAPI Agentic Intelligence & MCP Backend (hosted on Render), connected to a managed PostgreSQL database instance.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Vercel Edge Network                            │
│                  ORION Executive Operations Dashboard                   │
│                    (Next.js 14 / TypeScript / Tailwind)                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTPS (Configurable API Base URL)
                                     │ CORS Protected
┌────────────────────────────────────▼────────────────────────────────────┐
│                             Render Web Service                          │
│                          ORION FastAPI Backend Engine                   │
│                                                                         │
│  ┌───────────────────────┐  ┌────────────────────────────────────────┐  │
│  │   Analytics Engines   │  │       Multi-Agent Pipeline (Local)     │  │
│  │ (Revenue, Support...) │  │ (Detect, Evidence, Impact, Rec, Audit) │  │
│  └───────────┬───────────┘  └───────────────────┬────────────────────┘  │
│              │                                  │                       │
│  ┌───────────▼──────────────────────────────────▼────────────────────┐  │
│  │                     MCP Tool Layer (18 Tools)                     │  │
│  │              Model Context Protocol Tool Registry & Gate          │  │
│  └───────────────────────────────┬───────────────────────────────────┘  │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │ SQLAlchemy 2.0 (Sync Engine)
┌──────────────────────────────────▼──────────────────────────────────────┐
│                        Managed PostgreSQL Database                      │
│            (NovaCart 90-Day Synthetic Dataset + Audit Ledger)           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Current Architecture vs. Deployment Target

| Component | Local Development State | Public Demo Target | Key Delta |
|---|---|---|---|
| **Frontend Dashboard** | Next.js on `localhost:3000` | Next.js on **Vercel** (`https://<project>.vercel.app`) | Configurable `NEXT_PUBLIC_API_BASE_URL` |
| **Backend API** | FastAPI / Uvicorn on `127.0.0.1:8000` | FastAPI on **Render Web Service** (`0.0.0.0:$PORT`) | Dynamic port binding, env-driven CORS |
| **Database** | SQLite (`orion_verified.db`) / Local Postgres | **Managed PostgreSQL** (Render / Neon / Supabase) | `DATABASE_URL` support with connection normalization |
| **Agent Runtime** | `LocalAgentRuntime` (abstract interface) | `LocalAgentRuntime` (abstract interface) | **Preserved 100% on Python backend** |
| **MCP Tools** | 18 Tools across 5 safety tiers | 18 Tools across 5 safety tiers | **Preserved 100% on Python backend** |
| **Adya Integration** | `AdyaAgentRuntime` (Adapter-Ready Only) | `AdyaAgentRuntime` (Adapter-Ready Only) | **Explicitly documented as adapter-ready only** |
| **Governance & Safety** | Token-gated `WAITING_FOR_APPROVAL`, unapproved `EXECUTION_DENIED`, `SIMULATED ACTION` | Identical token governance & simulation sandbox | **Strictly enforced, zero external side-effects** |

---

## 3. Required Environment Variables

### Backend (Render)
| Variable | Required | Default / Example | Purpose |
|---|---|---|---|
| `PORT` | Auto-provided by Render | `8000` | Port for Uvicorn web server |
| `DATABASE_URL` | Yes (for Postgres) | `postgresql://user:pass@host:5432/dbname` | Connection string for PostgreSQL database |
| `ORION_CORS_ORIGINS` | Yes | `https://<your-vercel-app>.vercel.app,http://localhost:3000` | Comma-separated allowed frontend origins |
| `ORION_AGENT_PROVIDER` | No | `local` | Agent runtime provider (`local` / `adya`) |
| `ORION_APP_NAME` | No | `ORION` | Application brand name |
| `ORION_DEBUG` | No | `False` | Debug mode switch |

### Frontend (Vercel)
| Variable | Required | Default / Example | Purpose |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Yes | `https://<your-render-backend>.onrender.com` | Base URL of deployed FastAPI backend |

---

## 4. Database Migration & Seeding Plan

1. **Target Schema**: 8 core tables:
   - `customers`, `products`, `orders`, `inventory_snapshots`, `support_tickets`, `marketing_campaigns`, `anomalies`, `audit_events`.
2. **Schema Creation**: Automated upon startup or initialized via:
   ```bash
   python -m data.generate
   ```
   which detects `DATABASE_URL`, builds all tables, and populates the 52,000+ record NovaCart business operations incident dataset deterministically.
3. **Database URL Normalization**: Handles legacy `postgres://` prefixes emitted by some cloud providers (e.g. Render / Heroku) by converting to standard `postgresql://`.

---

## 5. Security & Governance Architecture

1. **Zero Secret Leakage**: No database passwords, server tokens, or private environment variables are prefixed with `NEXT_PUBLIC_` or exposed to the client.
2. **Strict CORS Policy**: Production backend restricts cross-origin resource sharing to the verified Vercel production domain. Local development URLs (`localhost:3000`) remain configurable for paired debugging.
3. **Immutable Safety Gates**:
   - Consequential operations remain gated at `WAITING_FOR_APPROVAL`.
   - Execution without a cryptographic approval token returns `EXECUTION_DENIED` with `HTTP 403 Forbidden`.
   - All executions operate exclusively in `SIMULATED ACTION` mode with rollback metadata saved to the immutable `audit_events` ledger.
4. **Adya Boundary**: Adya is explicitly marked **ADAPTER-READY ONLY**. No mock live connections or fake credentials are used.

---

## 6. Deployment Commands

### Render (Backend)
- **Build Command**: `pip install -r requirements.txt`
- **Pre-Deploy Command (Optional)**: `python -m data.generate`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Vercel (Frontend)
- **Root Directory**: `frontend`
- **Framework Preset**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

---

## 7. Known Public Demo Scope & Limitations

1. **Simulated Action Execution**: All automated remediation actions are executed in high-fidelity simulation mode. No live Shopify/Zendesk API webhooks are dispatched.
2. **Adya Connection**: Provider interface is complete and tested via adapter contract tests, awaiting live platform credentials for external orchestrator handover.
3. **Ephemeral Free Tier Sleeping**: If hosted on Render free tier, the first request after 15 minutes of inactivity may experience a 30-50s cold-start spin-up delay.
