"""
ORION MCP Live Demo & Client Verification Script

Executes the complete autonomous agent workflow using the MCP tool layer:
1. Tool Discovery & Classification
2. Anomaly Detection
3. Quantitative Evidence Retrieval
4. Deterministic Business Impact
5. Multi-Agent Autonomous Investigation
6. Prioritized Recommendations
7. Governance Gatekeeping & Rejection
8. Human Executive Approval
9. Safe Simulation Execution
10. Immutable Audit Trail Inspection
"""

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


def run_demo():
    print("==================================================================")
    print("      ORION MCP BUSINESS TOOL LAYER — LIVE CLIENT DEMO            ")
    print("==================================================================\n")

    # 1. Tool Discovery
    print("1. DISCOVERING AVAILABLE ORION MCP TOOLS:")
    for tool_name, safety in TOOL_SAFETY_CLASSIFICATIONS.items():
        print(f"  [OK] {tool_name:<30} (Safety: {safety})")
    print(f"Total Registered Tools: {len(TOOL_SAFETY_CLASSIFICATIONS)}\n")

    # 2. Query Anomalies
    print("2. AGENT QUERY: 'What critical business anomalies are currently occurring?'")
    anom_res = get_business_anomalies(severity="CRITICAL")
    anomalies = anom_res.get("anomalies", [])
    print(f"Found {len(anomalies)} critical operational anomalies:")
    for a in anomalies:
        print(
            f"  - [{a['anomaly_id']}] {a['metric']}: {a['current_value']:,.2f} "
            f"(Baseline: {a['baseline_value']:,.2f}, Change: {a['change_percentage']:.1f}%) "
            f"[Dimension: {a['affected_dimension']}]"
        )

    # 3. Select ANOM-REV-001 & Evidence Gathering
    target_id = "ANOM-REV-001"
    print(f"\n3. AGENT SELECTS: {target_id}")
    print(f"Calling get_anomaly_evidence('{target_id}')...")
    evidence = get_anomaly_evidence(target_id)
    rev_eval = evidence["revenue"]["evaluation_revenue"]
    rev_base = evidence["revenue"]["baseline_revenue"]
    rev_change = evidence["revenue"]["change_percentage"]
    sla_breach = evidence["support"]["evaluation_sla_breach_rate"]
    stockout_elec = evidence["inventory"]["stockout_rate_by_category"].get("Electronics", 0.0)
    print(f"  - Revenue: ${rev_eval:,.2f} vs Base ${rev_base:,.2f} ({rev_change:.1f}%)")
    print(f"  - Support SLA Breach Rate: {sla_breach * 100:.1f}%")
    print(f"  - Electronics Stockout Rate: {stockout_elec * 100:.1f}%")

    # 4. Deterministic Business Impact
    print(f"\n4. DETERMINISTIC BUSINESS IMPACT CALCULATION:")
    impact = calculate_business_impact(target_id)
    print(f"  - Realized Revenue Loss: ${impact['realized_revenue_loss']:,.2f}")
    print(f"  - Daily Shortfall: ${impact['daily_revenue_shortfall']:,.2f}/day")
    print(f"  - Projected 30-Day Forward Risk: ${impact['projected_30d_risk']:,.2f}")
    print(f"  - Affected Customer Accounts: {impact['affected_customers_count']}")

    # 5. Multi-Agent Investigation
    print(f"\n5. TRIGGERING MULTI-AGENT INVESTIGATION PIPELINE:")
    inv_res = start_investigation(target_id)
    inv_id = inv_res["investigation_id"]
    print(f"  - Investigation ID: {inv_id}")
    print(f"  - Status: {inv_res['status']}")
    print(f"  - Confidence Score: {inv_res['confidence_score']:.2f}")
    if inv_res.get("root_causes"):
        rc = inv_res["root_causes"][0]
        print(f"  - Primary Root Cause: {rc['description'][:110]}...")

    # 6. Retrieve Recommendations
    print(f"\n6. RETRIEVING RANKED REMEDIATION RECOMMENDATIONS:")
    recs_res = get_recommendations(inv_id)
    recs = recs_res.get("recommendations", [])
    for r in recs:
        print(
            f"  [Priority {r['priority']}] {r['recommendation_id']}: {r['title']} "
            f"(Action: {r['action_type']}, Status: {r['approval_status']})"
        )

    # 7. Governance Enforcement — Unapproved Execution Blocked
    print(f"\n7. TESTING GOVERNANCE GATEKEEPER (Unapproved Execution Attempt):")
    unapproved_exec = execute_approved_action(
        action_id="ACT-REC-001",
        approval_id="APPR-UNAPPROVED-FAKE",
    )
    print(f"  Result: {unapproved_exec['status'].upper()} -> {unapproved_exec['error']}")

    # 8. Rejection Workflow Test
    if len(recs) >= 2:
        rec_2 = recs[1]["recommendation_id"]
        print(f"\n8. TESTING OPERATOR REJECTION on {rec_2}:")
        reject_res = reject_recommendation(
            recommendation_id=rec_2,
            approver="WarehouseOpsDirector",
            reason="Postponed due to current warehouse freight logistics constraints",
        )
        print(f"  Result: Status={reject_res['status']}, Message={reject_res['message']}")

        # Verify execution is blocked after rejection
        blocked_exec = execute_approved_action(
            action_id=f"ACT-{rec_2}",
            approval_id=reject_res["approval_id"],
        )
        print(f"  Execution Attempt After Rejection: {blocked_exec['status'].upper()} -> {blocked_exec['error']}")

    # 9. Human Executive Approval & Safe Simulation Execution
    rec_1 = recs[0]["recommendation_id"]
    print(f"\n9. FORMAL HUMAN APPROVAL & SAFE ACTION SIMULATION on {rec_1}:")
    appr_res = approve_recommendation(
        recommendation_id=rec_1,
        approver="ChiefOperationsOfficer",
        reason="Approved emergency tier-1 support capacity expansion",
    )
    print(f"  Approval Granted: ID={appr_res['approval_id']}, Status={appr_res['status']}")

    sim_res = execute_approved_action(
        action_id=f"ACT-{rec_1}",
        approval_id=appr_res["approval_id"],
        parameters={"agents_to_add": 15},
    )
    print(f"  Execution Completed: ID={sim_res['execution_id']}, Mode={sim_res['execution_mode']}")
    print("  Simulated Operational Changes:")
    for change in sim_res["result"].get("changes_made", []):
        print(f"    [+] {change}")

    # 10. Audit Trail
    print(f"\n10. IMMUTABLE OPERATIONS AUDIT TRAIL:")
    audit_res = get_audit_events(limit=8)
    for ev in audit_res.get("audit_events", [])[:6]:
        print(
            f"  [{ev['event_type']:<22}] Entity: {ev['entity_type']}:{ev['entity_id']:<15} "
            f"Actor: {ev['actor']:<20} Status: {ev['status']}"
        )

    print("\n==================================================================")
    print("   [OK] ORION MCP BUSINESS TOOL LAYER VERIFICATION COMPLETE       ")
    print("==================================================================")


if __name__ == "__main__":
    run_demo()
