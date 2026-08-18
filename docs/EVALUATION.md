# ORION — Evaluation Framework

## 1. Overview

ORION's evaluation framework validates that the system correctly detects
anomalies, investigates root causes, and produces actionable recommendations.
Because agents reason over deterministic data, evaluation focuses on both
the accuracy of data analytics AND the quality of agent reasoning.

## 2. Evaluation Dimensions

### 2.1 Anomaly Detection Accuracy

| Metric              | Description                                     | Target   |
|---------------------|-------------------------------------------------|----------|
| True Positive Rate  | Correctly detected engineered anomalies         | > 95%    |
| False Positive Rate | Spurious anomalies flagged                      | < 10%    |
| Detection Latency   | Time from anomaly onset to detection            | < 1 day  |
| Severity Accuracy   | Correct severity classification                 | > 90%    |

### 2.2 Investigation Completeness

| Metric                  | Description                                 | Target   |
|-------------------------|---------------------------------------------|----------|
| Dimension Coverage      | % of relevant dimensions investigated       | 100%     |
| Data Retrieval Success  | All queries return valid results             | 100%     |
| Pipeline Completion     | Investigation runs all agents to completion  | > 95%    |
| Timeline Accuracy       | All steps logged with correct timestamps     | 100%     |

### 2.3 Root Cause Accuracy

| Metric                  | Description                                 | Target   |
|-------------------------|---------------------------------------------|----------|
| Primary Cause Identified| Engineered root cause in top-3 hypotheses   | > 90%    |
| Evidence Quality        | All evidence traceable to data queries       | 100%     |
| Confidence Calibration  | Confidence scores correlate with accuracy    | r > 0.7  |
| Causal Chain Validity   | Causal relationships are logically sound     | > 85%    |

### 2.4 Business Impact Accuracy

| Metric                  | Description                                 | Target   |
|-------------------------|---------------------------------------------|----------|
| Revenue Impact Accuracy | Within 15% of ground truth (engineered data)| > 85%    |
| Churn Estimate Accuracy | Within 20% of actual churn count            | > 80%    |
| Projection Reasonability| Projections within historical variance      | > 90%    |

### 2.5 Recommendation Quality

| Metric                  | Description                                 | Target   |
|-------------------------|---------------------------------------------|----------|
| Relevance               | Recommendations address identified causes   | > 90%    |
| Actionability           | Recommendations are implementable           | > 85%    |
| Prioritization          | Highest-impact actions ranked first         | > 80%    |
| Completeness            | All critical actions included               | > 85%    |

### 2.6 System Performance

| Metric                  | Description                                 | Target   |
|-------------------------|---------------------------------------------|----------|
| End-to-end Latency      | Full investigation completion time          | < 60s    |
| API Response Time (p95)  | Individual API call latency                | < 500ms  |
| Dashboard Load Time     | Initial dashboard render                    | < 2s     |

## 3. Test Scenarios

### 3.1 Primary Scenario: Support + Inventory Revenue Decline

**Engineered incident**:
- Support response times degrade from 2h → 18h over 30 days
- Key product categories experience stockouts (3 of 8 categories)
- Repeat purchase rate drops from 34% → 21%
- Total revenue declines 23% over 60 days

**Expected system output**:
1. ✅ Anomaly detected: Revenue decline of ~23%
2. ✅ Investigation covers all 10 dimensions
3. ✅ Root cause #1: Support SLA degradation → customer churn
4. ✅ Root cause #2: Inventory stockouts → lost sales
5. ✅ Compounding effect identified
6. ✅ Impact quantified: Revenue loss within 15% of actual
7. ✅ Recommendations: Hire support staff, emergency restock, retention campaign
8. ✅ Actions require human approval
9. ✅ Full audit trail

### 3.2 Edge Cases

| Scenario                        | Expected Behavior                        |
|---------------------------------|------------------------------------------|
| No anomaly present              | No false positive detection              |
| Multiple simultaneous anomalies | Each investigated independently          |
| Partial data availability       | Graceful degradation with data quality flag|
| Agent timeout                   | Partial results returned, flagged        |
| Approval timeout                | Escalation triggered per policy          |

## 4. Evaluation Methodology

### 4.1 Ground Truth Dataset

The synthetic dataset includes **engineered ground truth** with known:
- Anomaly onset dates and magnitudes
- Root cause parameters (e.g., support staffing reduction date)
- Expected impact calculations
- Correct causal relationships

### 4.2 Automated Evaluation Pipeline

```python
# evaluation/run_evaluation.py

class EvaluationSuite:
    """Automated evaluation of ORION's investigation pipeline."""

    def evaluate_detection(self, anomalies, ground_truth):
        """Compare detected anomalies against ground truth."""

    def evaluate_investigation(self, investigation, ground_truth):
        """Assess investigation completeness and accuracy."""

    def evaluate_root_causes(self, hypotheses, ground_truth):
        """Check if engineered root causes are identified."""

    def evaluate_impact(self, impact_report, ground_truth):
        """Compare impact estimates against known values."""

    def evaluate_recommendations(self, recommendations, ground_truth):
        """Assess recommendation relevance and completeness."""

    def generate_report(self) -> EvaluationReport:
        """Generate comprehensive evaluation report."""
```

### 4.3 Human Evaluation

For agent reasoning quality (which cannot be fully automated):

- **Coherence**: Does the narrative make logical sense?
- **Completeness**: Are all relevant factors discussed?
- **Accuracy**: Are all stated facts verifiable from data?
- **Actionability**: Can a business leader act on the recommendations?

## 5. Evaluation Schedule

| Phase          | What is Evaluated                    | When              |
|----------------|--------------------------------------|-------------------|
| Unit tests     | Individual analytics functions       | Every commit      |
| Integration    | Full pipeline with synthetic data    | Every PR          |
| Scenario       | Primary demo scenario end-to-end     | Before demo       |
| Regression     | All scenarios after code changes     | Before release    |

## 6. Success Criteria for Sunday Demo

The proof-of-concept is considered successful if:

1. ✅ Anomaly in revenue is detected automatically
2. ✅ Investigation runs through all agents without errors
3. ✅ Root causes (support + inventory) are correctly identified
4. ✅ Business impact is quantified with reasonable accuracy
5. ✅ Recommendations are relevant and actionable
6. ✅ Human approval workflow is functional
7. ✅ Full audit trail is viewable
8. ✅ Dashboard displays investigation in real-time
9. ✅ No hallucinated data — all numbers traceable to SQL queries
10. ✅ End-to-end latency under 60 seconds
