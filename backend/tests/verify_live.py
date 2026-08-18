"""
Live end-to-end verification script for Milestone 3.
"""

import json
import urllib.error
import urllib.request

base_url = "http://127.0.0.1:8000/api/v1"


def post_json(path, data):
    url = f"{base_url}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode("utf-8"))


def get_json(path):
    url = f"{base_url}{path}"
    res = urllib.request.urlopen(url)
    return json.loads(res.read().decode("utf-8"))


def main():
    print("=== 1. TRIGGERING INVESTIGATION FOR ANOM-REV-001 ===")
    inv_out = post_json("/investigations", {"anomaly_id": "ANOM-REV-001"})
    inv_id = inv_out["investigation_id"]
    print(f"Investigation ID: {inv_id}")
    print(f"Status: {inv_out['status']}")
    print(f"Confidence: {inv_out['confidence_score']}")
    print(f"Primary Root Cause: {inv_out['root_causes'][0]['description'][:120]}...")
    print(f"Realized Revenue Loss: ${inv_out['business_impact']['total_revenue_loss']:,.2f}")
    print(f"Projected 30d Risk: ${inv_out['business_impact']['projected_30d_risk']:,.2f}")
    print(f"Timeline Steps Completed: {len(inv_out['timeline'])}")

    print("\n=== 2. FETCHING RECOMMENDATIONS ===")
    recs = get_json(f"/investigations/{inv_id}/recommendations")
    for r in recs:
        print(f"[{r['category'].upper()}] Priority {r['priority']}: {r['title']} (Action: {r['action_type']})")

    rec_1 = recs[0]
    rec_1_id = rec_1["recommendation_id"]
    rec_2 = recs[1]
    rec_2_id = rec_2["recommendation_id"]

    print("\n=== 3. VERIFYING UNAPPROVED EXECUTION IS BLOCKED ===")
    try:
        post_json(
            f"/actions/ACT-{rec_1_id}/execute",
            {
                "action_type": rec_1["action_type"],
                "approval_id": f"APPR-{rec_1_id}",
                "investigation_id": inv_id,
            },
        )
        print("ERROR: Unapproved action was not blocked!")
    except urllib.error.HTTPError as e:
        print(f"SUCCESS: Unapproved execution correctly rejected with HTTP {e.code}: {e.reason}")

    print("\n=== 4. TESTING REJECTION PATH ===")
    reject_res = post_json(
        f"/recommendations/{rec_2_id}/reject",
        {
            "decision_reason": "Postponed due to current warehouse logistics constraints",
            "decided_by": "WarehouseOpsDirector",
        },
    )
    print(f"Recommendation {rec_2_id} Status: {reject_res['status']}")

    try:
        post_json(
            f"/actions/ACT-{rec_2_id}/execute",
            {
                "action_type": rec_2["action_type"],
                "approval_id": f"APPR-{rec_2_id}",
                "investigation_id": inv_id,
            },
        )
        print("ERROR: Rejected action was executed!")
    except urllib.error.HTTPError as e:
        print(f"SUCCESS: Rejected action correctly blocked with HTTP {e.code}")

    print("\n=== 5. TESTING APPROVAL & SAFE ACTION EXECUTION ===")
    approve_res = post_json(
        f"/recommendations/{rec_1_id}/approve",
        {
            "decision_reason": "Emergency support staffing expansion approved by Chief Customer Officer",
            "decided_by": "CCO_Executive",
        },
    )
    print(f"Approval Granted: ID={approve_res['approval_id']}, Status={approve_res['status']}")

    exec_res = post_json(
        f"/actions/ACT-{rec_1_id}/execute",
        {
            "action_type": rec_1["action_type"],
            "approval_id": approve_res["approval_id"],
            "investigation_id": inv_id,
            "parameters": {"agents_to_add": 15},
        },
    )
    print(f"Action Execution: ID={exec_res['execution_id']}, Status={exec_res['status']}")
    print("Simulated Changes Made:")
    for change in exec_res["result"]["changes_made"]:
        print(f"  - {change}")

    print("\n=== 6. VERIFYING IMMUTABLE AUDIT TRAIL ===")
    audit_events = get_json("/audit?limit=15")
    print(f"Total Recent Audit Events: {len(audit_events)}")
    for ev in audit_events[:8]:
        print(f"  [{ev['event_type']}] entity={ev['entity_type']}:{ev['entity_id']} actor={ev['actor']} status={ev['status']}")


if __name__ == "__main__":
    main()
