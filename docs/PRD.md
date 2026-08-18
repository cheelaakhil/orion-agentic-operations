# ORION — Product Requirements Document

## 1. Product Vision

ORION is an AI-powered business operations intelligence system that
autonomously detects anomalies in business metrics, investigates root causes,
estimates business impact, recommends corrective actions, and enforces human
approval before executing consequential actions.

## 2. Problem Statement

Modern e-commerce businesses generate vast amounts of operational data across
revenue, inventory, support, marketing, and customer systems. When business
performance deteriorates:

- Anomalies are detected late (often days or weeks after onset)
- Root cause investigation is manual, slow, and error-prone
- Cross-functional signals (e.g., support quality affecting revenue) are missed
- Impact estimation is guesswork rather than data-driven
- No structured process exists for approving and tracking corrective actions

ORION solves this by providing an autonomous investigation pipeline that
reasons over **verified, structured data** — never hallucinated evidence.

## 3. Target Users

| Role                | Usage                                              |
|---------------------|----------------------------------------------------|
| VP of Operations    | Reviews investigation reports, approves actions    |
| Data Analyst        | Configures thresholds, validates agent findings    |
| Support Manager     | Receives support-specific insights and actions     |
| Marketing Manager   | Reviews marketing impact analysis                  |
| Engineering/DevOps  | Monitors system health and integration status      |

## 4. Primary Demo Scenario

A fictional e-commerce company ("NovaMart") experiences a **significant
revenue decline** over a 90-day period. The decline is caused by a
deliberately engineered business incident:

### Engineered Root Cause
1. **Support SLA degradation**: Average response times increase from 2 hours
   to 18+ hours due to understaffing during a growth period
2. **Inventory stockouts**: Key product categories experience stockouts due
   to supply chain delays
3. **Compounding effect**: Poor support drives down repeat purchase rates,
   while stockouts reduce new customer conversion

### Investigation Dimensions
ORION must investigate across all of these dimensions:

| Dimension           | What to Analyze                                    |
|---------------------|----------------------------------------------------|
| Revenue             | Daily/weekly trends, growth rates, anomaly onset   |
| Regions             | Geographic breakdown, region-specific drops        |
| Products            | Category-level performance, top movers/losers      |
| Customers           | New vs. returning, churn signals                   |
| Customer Segments   | Segment-level behavior changes                     |
| Repeat Purchases    | Retention rates, repeat purchase frequency         |
| Inventory           | Stock levels, stockout events, fulfillment rates   |
| Support Tickets     | Volume, resolution time, satisfaction scores       |
| Support SLA         | Response time compliance, escalation rates         |
| Marketing           | Campaign performance, attribution, CAC trends      |

## 5. Functional Requirements

### 5.1 Anomaly Detection
- FR-1: System monitors key business metrics on a configurable schedule
- FR-2: Statistical anomaly detection identifies significant deviations
- FR-3: Anomalies are classified by severity (critical, high, medium, low)
- FR-4: Each anomaly includes: metric, magnitude, onset date, confidence

### 5.2 Investigation Pipeline
- FR-5: Detected anomalies trigger an automated investigation
- FR-6: Investigation proceeds through a defined agent pipeline
- FR-7: Each agent produces structured, verifiable output
- FR-8: Investigation progress is visible in real-time on the dashboard

### 5.3 Root Cause Analysis
- FR-9: System generates ranked root-cause hypotheses
- FR-10: Each hypothesis includes supporting evidence from data
- FR-11: Confidence scores are based on statistical correlation, not LLM opinion
- FR-12: Cross-functional correlations are identified automatically

### 5.4 Business Impact Estimation
- FR-13: Impact is quantified in revenue/cost terms
- FR-14: Projections use deterministic models (not LLM-generated numbers)
- FR-15: Impact includes both realized losses and projected future impact

### 5.5 Recommendations
- FR-16: System generates prioritized action recommendations
- FR-17: Each recommendation includes expected impact and implementation cost
- FR-18: Recommendations are categorized: immediate, short-term, long-term

### 5.6 Human Approval
- FR-19: Consequential actions require explicit human approval
- FR-20: Approval UI shows full context: evidence, impact, risks
- FR-21: Approvers can approve, reject, or request more information
- FR-22: Approval decisions are logged immutably

### 5.7 Action Execution
- FR-23: Approved actions are executed through defined action handlers
- FR-24: Execution status is tracked and reported
- FR-25: Failed actions trigger alerts and rollback where possible

### 5.8 Audit Trail
- FR-26: Every detection, investigation step, recommendation, approval, and
  action is logged with timestamps and actor identity
- FR-27: Audit trail is immutable and queryable
- FR-28: Full investigation timeline is reconstructable from audit logs

## 6. Non-Functional Requirements

| Category       | Requirement                                          |
|----------------|------------------------------------------------------|
| Performance    | Investigation completes within 60 seconds            |
| Reliability    | Graceful degradation if agent layer is unavailable   |
| Security       | Role-based access control for approval workflows     |
| Auditability   | Immutable audit log for all system decisions         |
| Extensibility  | New agents and tools addable without core changes    |
| Integrability  | Adya integration via adapter pattern                 |

## 7. Out of Scope (v1)

- Real-time streaming data ingestion
- Multi-tenant support
- Mobile application
- Custom agent training
- Production deployment automation
