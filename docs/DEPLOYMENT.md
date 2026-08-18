# ORION — Public Demonstration Deployment Runbook

> Step-by-step guide for deploying the ORION Executive Operations Dashboard to **Vercel** and the FastAPI Agentic Intelligence & MCP Backend to **Render** with **Managed PostgreSQL**.

---

## 1. Architecture Overview

- **Frontend**: Next.js 14 App Router on **Vercel** (`https://<your-project>.vercel.app`)
- **Backend API**: Python 3.12 / FastAPI on **Render Web Service** (`https://<your-backend>.onrender.com`)
- **Database**: Managed PostgreSQL on **Render / Neon / Supabase**
- **Communication**: HTTPS REST API with environment-driven CORS governance
- **Governance**: Token-gated human approval (`WAITING_FOR_APPROVAL`), unapproved blocking (`EXECUTION_DENIED`), sandboxed `SIMULATED ACTION`

---

## 2. Step-by-Step Deployment Guide

### Step A: Provision Managed PostgreSQL Database

1. On **Render** (or **Neon** / **Supabase**):
   - Click **New** → **PostgreSQL**.
   - Name: `orion-postgres`
   - Database: `orion`
   - User: `orion`
   - Plan: Free / Starter
2. Copy the **Internal Database URL** (if deploying backend on Render in the same region) or **External Connection String**:
   ```
   postgresql://orion:<password>@<host>:5432/orion
   ```

---

### Step B: Deploy Backend to Render

1. Log into [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Web Service**.
2. Connect your GitHub repository: `https://github.com/cheelaakhil/orion-agentic-operations`.
3. Configure settings:
   - **Name**: `orion-backend`
   - **Region**: Same region as your database (e.g. `Oregon`)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
4. Add **Environment Variables**:
   | Variable | Value |
   |---|---|
   | `PYTHON_VERSION` | `3.12.0` |
   | `DATABASE_URL` | `postgresql://orion:<password>@<host>:5432/orion` |
   | `ORION_CORS_ORIGINS` | `https://*.vercel.app,http://localhost:3000` *(update with exact Vercel URL once known)* |
   | `ORION_AGENT_PROVIDER` | `local` |
5. Click **Deploy Web Service**.

---

### Step C: Initialize & Seed Database

Once the Render backend service is provisioned:

1. Open the Render **Shell** tab on your backend service (or run locally with the remote `DATABASE_URL`):
   ```bash
   python -m data.generate
   ```
2. This generates the 52,000+ record NovaCart business operations dataset with 90 days of synthetic transactions, ticket logs, stockout events, and the engineered anomaly incident.

---

### Step D: Verify Backend Health

Test your live backend in browser or via curl:

```bash
# Health endpoint
curl https://<your-backend>.onrender.com/api/v1/health

# Expected response:
# {"status":"healthy","service":"orion-backend","version":"0.3.0"}

# Active Anomalies endpoint
curl https://<your-backend>.onrender.com/api/v1/anomalies
```

---

### Step E: Deploy Frontend to Vercel

1. Log into [Vercel Dashboard](https://vercel.com/) and click **Add New...** → **Project**.
2. Import the GitHub repository: `cheelaakhil/orion-agentic-operations`.
3. Configure project settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: Click *Edit* and select **`frontend`**
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
4. Add **Environment Variables**:
   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_BASE_URL` | `https://<your-backend>.onrender.com` |
5. Click **Deploy**.

---

### Step F: Update CORS on Backend

Once your Vercel URL is generated (e.g. `https://orion-agentic-operations.vercel.app`):
1. In Render Dashboard → `orion-backend` → **Environment**.
2. Update `ORION_CORS_ORIGINS`:
   ```
   https://orion-agentic-operations.vercel.app,https://*.vercel.app,http://localhost:3000
   ```
3. Save changes (Render will trigger a zero-downtime rolling restart).

---

## 3. Post-Deployment Verification Checklist

1. [ ] **Executive Dashboard**: Open `https://<your-project>.vercel.app` — verify dark glassmorphism dashboard loads with active KPI cards.
2. [ ] **Anomaly Dossier**: Click on **ANOM-REV-001** incident card — verify multi-dimensional evidence dossier loads.
3. [ ] **Agent Run (MCP)**: Click on **Agent Run (MCP)** in sidebar:
   - Click **Start Agent Investigation (ANOM-REV-001)**.
   - Verify trace steps stream from `DETECT` to `RECOMMEND`.
   - Verify workflow halts at **WAITING FOR APPROVAL** state.
   - Click **Approve & Simulate Action**.
   - Verify execution completes strictly in **SIMULATED ACTION** mode.
4. [ ] **Audit Trail**: Open **Audit Log** tab — verify approval token and simulation execution events are recorded.

---

## 4. Troubleshooting Guide

### Issue: Frontend displays "Failed to fetch" or Network Error
- **Cause**: CORS origin mismatch or backend sleeping on Render free tier.
- **Fix**: Check `ORION_CORS_ORIGINS` in Render environment variables. If on free tier, allow 30-50 seconds for the backend instance to spin up from cold sleep.

### Issue: Database connection error on Render startup
- **Cause**: Cloud provider using deprecated `postgres://` connection scheme.
- **Fix**: ORION automatically normalizes `postgres://` to `postgresql://` in `backend/core/database.py`. Ensure password special characters are URL-encoded if applicable.

### Issue: "Not Found" on Agent Run endpoints
- **Cause**: Incorrect API base URL configuration in frontend.
- **Fix**: Verify `NEXT_PUBLIC_API_BASE_URL` in Vercel settings points to `https://<backend>.onrender.com` (without trailing slashes).
