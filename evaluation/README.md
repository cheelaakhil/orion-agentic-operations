# ORION Evaluation Suite

This directory contains evaluation benchmarks, scenario runners, and verification harnesses for the ORION investigation pipeline.

## Evaluation Goals

1. **Verify Deterministic Analytics**: Ensure SQL queries and Python calculations accurately detect anomalies and compute metrics without hallucination.
2. **Benchmark Root-Cause Precision**: Validate that the agent reasoning correctly ranks the engineered root causes (Support SLA + Stockouts) in the top hypotheses.
3. **Audit Trail Completeness**: Ensure 100% of pipeline decisions, inputs, and outputs are immutably logged with trace IDs.
4. **Human-in-the-Loop Governance**: Validate that zero consequential actions are triggered without explicit approval.

## Structure

```
evaluation/
├── benchmarks/      # Ground truth metrics and scenario definitions
├── harness/         # Automated test runners for agent pipeline
├── metrics/         # Accuracy, latency, and calibration scoring
└── README.md
```

See [EVALUATION.md](../docs/EVALUATION.md) for full evaluation metrics and criteria.
