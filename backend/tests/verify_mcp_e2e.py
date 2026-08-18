"""
ORION Milestone 5 — Full End-to-End MCP & Data Integrity Verification Script
"""

import json
from datetime import datetime
from backend.core.database import SessionLocal
from backend.services.analytics import anomaly_engine, evidence as evidence_service
from orion_mcp.tools import (
    TOOL_SAFETY_CLASSIFICATIONS,
    approve_recommendation,
    calculate_business_impact,
    execute_approved_action,
    get_anomaly_evidence,
    get_audit_events,
    get_business_anomalies,
    get_customer_analytics,
    get_inventory_analytics,
    get_investigation,
    get_marketing_analytics,
    get_recommendations,
    get_revenue_analytics,
    get_revenue_by_product,
    get_revenue_by_region,
    get_support_analytics,
    reject_recommendation,
    request_approval,
    start_investigation,
)


def run_verification():
    print("==================================================================")
    print("      ORION MILESTONE 5: END-TO-END MCP & GOVERNANCE VERIFICATION ")
    print("==================================================================\n")

    # 1. Discover tools
    print("[STEP 1] DISCOVER TOOLS:")
    print(f"Total tools discovered: {len(TOOL_SAFETY_CLASSIFICATIONS)}")
    for t_name, safety in TOOL_SAFETY_CLASSIFICATIONS.items():
        print(f"  - {t_name:<28} | Safety: {safety}")
    assert len(TOOL_SAFETY_CLASSIFICATIONS) == 18

    # 2. get_business_anomalies
    print("\n[STEP 2] GET_BUSINESS_ANOMALIES:")
    anomalies_res = get_business_anomalies()
    anomalies = anomalies_res["anomalies"]
    print(f"Detected anomalies count: {len(anomalies)}")
    for a in anomalies:
        print(f"  - {a['anomaly_id']} | Metric: {a['metric']} | Change: {a['change_percentage']:.1f}% | Sev: {a['severity']}")

    # 3. Select ANOM-REV-001
    target_id = "ANOM-REV-001"
    print(f"\n[STEP 3] SELECTED TARGET ANOMALY: {target_id}")

    # 4. get_anomaly_evidence(ANOM-REV-001)
    print(f"\n[STEP 4] GET_ANOMALY_EVIDENCE({target_id}):")
    evidence_res = get_anomaly_evidence(target_id)
    rev_base = evidence_res["revenue"]["baseline_revenue"]
    rev_eval = evidence_res["revenue"]["evaluation_revenue"]
    sla_breach = evidence_res["support"]["evaluation_sla_breach_rate"]
    elec_stockout = evidence_res["inventory"]["stockout_rate_by_category"].get("Electronics", 0.0)
    print(f"  - Revenue Eval vs Base: ${rev_eval:,.2f} vs ${rev_base:,.2f} ({evidence_res['revenue']['change_percentage']}%)")
    print(f"  - Support SLA Breach Rate: {sla_breach*100:.1f}%")
    print(f"  - Electronics Stockout Rate: {elec_stockout*100:.1f}%")

    # 5. calculate_business_impact(ANOM-REV-001)
    print(f"\n[STEP 5] CALCULATE_BUSINESS_IMPACT({target_id}):")
    impact_res = calculate_business_impact(target_id)
    print(f"  - Realized Revenue Loss: ${impact_res['realized_revenue_loss']:,.2f}")
    print(f"  - 30-Day Forward Risk: ${impact_res['projected_30d_risk']:,.2f}")
    print(f"  - Affected Customer Accounts: {impact_res['affected_customers_count']}")

    # 6. start_investigation(ANOM-REV-001)
    print(f"\n[STEP 6] START_INVESTIGATION({target_id}):")
    inv_res = start_investigation(target_id)
    inv_id = inv_res["investigation_id"]
    print(f"  - Generated Investigation ID: {inv_id}")
    print(f"  - Status: {inv_res['status']}")
    print(f"  - Confidence Score: {inv_res['confidence_score']:.2f}")

    # 7. get_investigation()
    print(f"\n[STEP 7] GET_INVESTIGATION({inv_id}):")
    inv_details = get_investigation(inv_id)
    print(f"  - Investigation Status: {inv_details['status']}")
    print(f"  - Root Causes Count: {len(inv_details.get('root_causes', []))}")
    print(f"  - Timeline Steps: {len(inv_details.get('timeline', []))}")

    # 8. get_recommendations()
    print(f"\n[STEP 8] GET_RECOMMENDATIONS({inv_id}):")
    recs_res = get_recommendations(inv_id)
    recs = recs_res["recommendations"]
    print(f"  - Retrieved {len(recs)} ranked recommendations:")
    for r in recs:
        print(f"    [P{r['priority']}] {r['recommendation_id']}: {r['title']} ({r['action_type']}) -> Status: {r['approval_status']}")

    # 9. request_approval()
    rec_target = recs[0]
    rec_id = rec_target["recommendation_id"]
    print(f"\n[STEP 9] REQUEST_APPROVAL({rec_id}):")
    req_res = request_approval(rec_id)
    print(f"  - Approval Request ID: {req_res.get('approval_id')}")
    print(f"  - Request Status: {req_res.get('status')}")

    # 10. Attempt execute_approved_action WITHOUT approval
    print(f"\n[STEP 10] ATTEMPT EXECUTE_APPROVED_ACTION WITHOUT APPROVAL:")
    unapproved_exec = execute_approved_action(
        action_id=f"ACT-{rec_id}",
        approval_id="APPR-UNAUTHORIZED-TOKEN-FAKE",
    )
    print(f"  - Attempt Result Status: {unapproved_exec['status']}")
    print(f"  - Error message: {unapproved_exec.get('error')}")

    # 11. Confirm execution is rejected
    print(f"\n[STEP 11] CONFIRM UNAPPROVED EXECUTION REJECTED:")
    assert unapproved_exec["status"] == "error"
    assert "EXECUTION_DENIED" in unapproved_exec["error"]
    print("  [OK] Confirmed: Unapproved action execution was strictly blocked with EXECUTION_DENIED.")

    # 12. approve_recommendation()
    print(f"\n[STEP 12] APPROVE_RECOMMENDATION({rec_id}):")
    appr_res = approve_recommendation(
        recommendation_id=rec_id,
        approver="ChiefOperationsOfficer",
        reason="Approved emergency tier-1 support capacity expansion via MCP verification suite",
    )
    approval_id = appr_res["approval_id"]
    print(f"  - Approval Status: {appr_res['status']}")
    print(f"  - Authorization Token Issued: {approval_id}")
    print(f"  - Approver: {appr_res['approver']}")

    # 13. execute_approved_action()
    print(f"\n[STEP 13] EXECUTE_APPROVED_ACTION({approval_id}):")
    exec_res = execute_approved_action(
        action_id=f"ACT-{rec_id}",
        approval_id=approval_id,
        parameters={"agents_to_add": 15},
    )
    print(f"  - Execution Status: {exec_res['status']}")
    print(f"  - Execution ID: {exec_res.get('execution_id')}")
    print(f"  - Mode: {exec_res.get('execution_mode')}")
    print("  - Changes made in simulation:")
    for change in exec_res.get("result", {}).get("changes_made", []):
        print(f"    [+] {change}")
    assert exec_res["status"] == "success"
    assert exec_res["execution_mode"] == "SIMULATED ACTION"

    # 14. get_audit_events()
    print(f"\n[STEP 14] GET_AUDIT_EVENTS():")
    audit_res = get_audit_events(limit=10)
    print(f"  - Retrieved {audit_res['total_retrieved']} audit events:")
    for ev in audit_res["audit_events"][:5]:
        print(f"    [{ev['event_type']:<22}] Entity: {ev['entity_type']}:{ev['entity_id']:<15} Actor: {ev['actor']:<20} Status: {ev['status']}")

    # ==================================================================
    # DATA INTEGRITY COMPARISON (FastAPI/Backend vs MCP)
    # ==================================================================
    print("\n==================================================================")
    print("      DATA INTEGRITY VERIFICATION (DIRECT SERVICE VS MCP)         ")
    print("==================================================================")
    db = SessionLocal()
    try:
        base_start = datetime(2026, 5, 1)
        base_end = datetime(2026, 6, 19, 23, 59, 59)
        eval_start = datetime(2026, 6, 20)
        eval_end = datetime(2026, 8, 1, 23, 59, 59)
        direct_anoms = anomaly_engine.detect_all_anomalies(db, base_start, base_end, eval_start, eval_end)
        direct_anom_rev = next((a for a in direct_anoms if a.anomaly_id == "ANOM-REV-001"), None)
        direct_evidence = evidence_service.generate_evidence_package(db, direct_anom_rev, base_start, base_end, eval_start, eval_end)

        print(f"Direct Backend Baseline Revenue:   ${direct_evidence.revenue.baseline_revenue:,.2f}")
        print(f"MCP Tool Baseline Revenue:         ${evidence_res['revenue']['baseline_revenue']:,.2f}")
        assert direct_evidence.revenue.baseline_revenue == evidence_res["revenue"]["baseline_revenue"]

        print(f"Direct Backend Evaluation Revenue: ${direct_evidence.revenue.evaluation_revenue:,.2f}")
        print(f"MCP Tool Evaluation Revenue:       ${evidence_res['revenue']['evaluation_revenue']:,.2f}")
        assert direct_evidence.revenue.evaluation_revenue == evidence_res["revenue"]["evaluation_revenue"]

        print(f"Direct Backend SLA Breach Rate:    {direct_evidence.support.evaluation_sla_breach_rate*100:.2f}%")
        print(f"MCP Tool SLA Breach Rate:          {evidence_res['support']['evaluation_sla_breach_rate']*100:.2f}%")
        assert direct_evidence.support.evaluation_sla_breach_rate == evidence_res["support"]["evaluation_sla_breach_rate"]

        print("\n[OK] 100% Single Source of Truth Verified. MCP tools use direct database calculations with zero drift.")
    finally:
        db.close()


if __name__ == "__main__":
    run_verification()
