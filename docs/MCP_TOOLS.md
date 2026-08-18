# ORION — Model Context Protocol (MCP) Business Tool Layer

## 1. Overview

ORION exposes its verified business analytics, multi-agent autonomous investigation pipeline, human governance state machine, and safe operational simulation capabilities through the **Model Context Protocol (MCP)**.

This enables external agentic runtimes (including **Adya** or other LLM orchestrators) to discover, inspect, and invoke ORION's operational capabilities in a standardized, provider-agnostic manner.

---

## 2. Security Boundary & Authoritative Principles

1. **MCP is an Interface Layer**: The underlying database, SQL aggregations, and business logic remain the authoritative source of truth.
2. **Deterministic Computations**: Tools execute deterministic queries and algorithms. The MCP layer does **NOT** allow an LLM or external agent to supply, fabricate, or manipulate business calculations.
3. **Strict Human Governance**: No consequential operational action may execute without explicit human executive approval (`APPROVAL_REQUESTED` → `ACTION_APPROVED`).
4. **Safe Simulation Enforcement**: All action executions run in controlled simulation mode (`SIMULATED ACTION`), producing audit logs without destructive production side effects.
5. **Immutable Audit Trail**: All agent invocations, human decisions, and action execution traces are permanently recorded in `audit_events`.

---

## 3. Tool Safety Classification Matrix

| Tool Name | Safety Classification | Mutates State | Approval Required | Description |
|---|---|---|---|---|
| `get_business_anomalies` | **`READ_ONLY`** | No | No | Retrieve detected operational anomalies across revenue, support, inventory, marketing. |
| `get_anomaly_evidence` | **`READ_ONLY`** | No | No | Fetch verified multi-dimensional quantitative evidence package. |
| `get_revenue_analytics` | **`READ_ONLY`** | No | No | Query gross revenue, order volumes, AOV, and daily timeseries. |
| `get_revenue_by_region` | **`READ_ONLY`** | No | No | Regional revenue distribution across North, South, East, West. |
| `get_revenue_by_product` | **`READ_ONLY`** | No | No | Category revenues (Electronics, Home, Apparel) and top SKUs. |
| `get_customer_analytics` | **`READ_ONLY`** | No | No | Repeat purchase rates, customer cohorts, and churn risks. |
| `get_support_analytics` | **`READ_ONLY`** | No | No | Ticket volumes, resolution hours, SLA breach rates, CSAT. |
| `get_inventory_analytics` | **`READ_ONLY`** | No | No | Warehouse stockout rates, category shortages, low stock signals. |
| `get_marketing_analytics` | **`READ_ONLY`** | No | No | Ad spend, impressions, CTR, conversion rates, ROAS. |
| `start_investigation` | **`ANALYSIS`** | Yes (DB) | No | Execute multi-agent causal investigation pipeline for an anomaly. |
| `get_investigation` | **`READ_ONLY`** | No | No | Retrieve investigation results, root causes, timeline, and impact. |
| `calculate_business_impact` | **`ANALYSIS`** | No | No | Compute deterministic realized revenue loss and 30d/90d forward risk. |
| `get_recommendations` | **`PROPOSAL`** | No | No | Retrieve ranked remediation proposals with recovery estimates. |
| `request_approval` | **`PROPOSAL`** | Yes (DB) | No | Create pending approval request (`PENDING_APPROVAL`). |
| `approve_recommendation` | **`APPROVAL`** | Yes (DB) | **Yes** | Formally authorize proposal and issue execution token (`APPROVED`). |
| `reject_recommendation` | **`APPROVAL`** | Yes (DB) | **Yes** | Formally reject proposal and block execution (`REJECTED`). |
| `execute_approved_action` | **`CONSEQUENTIAL_ACTION`** | Yes (DB) | **Yes** | Execute authorized safe simulation (fails if unapproved/rejected). |
| `get_audit_events` | **`READ_ONLY`** | No | No | Query chronological operations audit log with full event payloads. |

---

## 4. Detailed Tool Specifications

### 4.1 `get_business_anomalies`
- **Classification**: `READ_ONLY`
- **Inputs**:
  - `severity` *(optional, string)*: Filter by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Output**:
  ```json
  {
    "anomalies": [
      {
        "anomaly_id": "ANOM-REV-001",
        "metric": "daily_revenue",
        "current_value": 163189.54,
        "baseline_value": 286343.91,
        "change_absolute": -123154.37,
        "change_percentage": -43.01,
        "severity": "CRITICAL",
        "affected_dimension": "revenue"
      }
    ],
    "total_detected": 3
  }
  ```

### 4.2 `get_anomaly_evidence`
- **Classification**: `READ_ONLY`
- **Inputs**:
  - `anomaly_id` *(string, required)*: e.g. `"ANOM-REV-001"`.
- **Output**: Complete verified `EvidencePackage` across Revenue, Support, Inventory, Customers, and Marketing.

### 4.3 `start_investigation`
- **Classification**: `ANALYSIS`
- **Inputs**:
  - `anomaly_id` *(string, required)*: e.g. `"ANOM-REV-001"`.
- **Output**:
  ```json
  {
    "investigation_id": "INV-F7854170",
    "status": "awaiting_approval",
    "anomaly_id": "ANOM-REV-001",
    "confidence_score": 0.88,
    "summary": "Identified primary contributing factor: Support SLA breakdown & Category Stockouts.",
    "root_causes": [...],
    "business_impact": {
      "total_revenue_loss": 7300045.62,
      "projected_30d_risk": 5093055.00,
      "customer_churn_count": 813
    },
    "recommendations_count": 4,
    "timeline_steps": 5
  }
  ```

### 4.4 `calculate_business_impact`
- **Classification**: `ANALYSIS`
- **Inputs**:
  - `anomaly_id` *(string, optional, default `"ANOM-REV-001"`)*.
- **Output**: Realized revenue loss (`$7.30M`), projected 30d risk (`$5.09M`), affected customer count (`813`), and daily revenue shortfall (`$123.15k/day`).

### 4.5 `get_recommendations`
- **Classification**: `PROPOSAL`
- **Inputs**:
  - `investigation_id` *(string, optional)*.
- **Output**: List of prioritized recommendations with expected recovery ($1.45M – $2.10M), action types (`adjust_support_staffing`, `trigger_inventory_reorder`, `create_retention_campaign`, `adjust_marketing_budget`), and approval statuses.

### 4.6 `approve_recommendation`
- **Classification**: `APPROVAL`
- **Inputs**:
  - `recommendation_id` *(string, required)*: e.g. `"REC-001"`.
  - `approver` *(string, default `"ExecutiveOpsDirector"`)*.
  - `reason` *(string, default `"Approved via ORION MCP Governance Tool"`)*.
- **Output**: Generated authorization token `approval_id: "APPR-REC-001"` and status `"APPROVED"`.

### 4.7 `reject_recommendation`
- **Classification**: `APPROVAL`
- **Inputs**:
  - `recommendation_id` *(string, required)*: e.g. `"REC-002"`.
  - `approver` *(string, default `"ExecutiveOpsDirector"`)*.
  - `reason` *(string, required)*.
- **Output**: Status `"REJECTED"` permanently blocking action execution.

### 4.8 `execute_approved_action`
- **Classification**: `CONSEQUENTIAL_ACTION`
- **Inputs**:
  - `action_id` *(string, required)*: e.g. `"ACT-REC-001"`.
  - `approval_id` *(string, required)*: e.g. `"APPR-REC-001"`.
  - `investigation_id` *(string, optional)*.
  - `parameters` *(object, optional)*.
- **Enforcement Rules**:
  - Rejects with error if `approval_id` is missing.
  - Rejects with error if approval is not in `APPROVED` status.
  - Rejects with error if recommendation was previously `REJECTED`.
  - Rejects with error if action was already executed.
- **Output**:
  ```json
  {
    "status": "success",
    "execution_id": "EXEC-69F950F2",
    "execution_mode": "SIMULATED ACTION",
    "result": {
      "changes_made": [
        "Simulated assignment of 15 Tier-1/Tier-2 support specialists",
        "Simulated automated triage macro deployment",
        "Simulated queue throughput increase from 42 to 128 tickets/hr"
      ],
      "metrics_affected": ["support_sla_breach_rate", "avg_resolution_hours", "customer_csat"]
    }
  }
  ```

---

## 5. Local Server Execution

### Run with Python MCP SDK (stdio transport)
```bash
python -m mcp.server
```

### Run with FastMCP CLI
```bash
mcp run mcp/server.py
```
