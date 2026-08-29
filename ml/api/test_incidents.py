"""
Test and Verification Suite for YatraSafe Alert & Incident Command Center.
"""

import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def make_request(method: str, path: str, data: dict = None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"} if data else {}
    body = json.dumps(data).encode("utf-8") if data else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))


def test_incident_lifecycle():
    print("=" * 80)
    print(">> TESTING INCIDENT COMMAND CENTER LIFECYCLE")
    print("=" * 80)

    # 1. Trigger Emergency Overcrowding Scenario to generate 4 Critical Pavagadh alerts
    print("\n[Step 1] Triggering Emergency Overcrowding scenario...")
    status, demo_data = make_request("GET", "/api/demo/emergency-overcrowding")
    assert status == 200, f"Expected 200, got {status}"
    alerts_count = len(demo_data.get("intelligence", {}).get("alerts", []))
    print(f"  • Demo scenario executed successfully. Triggered {alerts_count} critical alerts.")

    # 2. Fetch Active Incidents
    print("\n[Step 2] Fetching active incidents from GET /api/incidents/active...")
    status, active_data = make_request("GET", "/api/incidents/active")
    assert status == 200, f"Expected 200, got {status}"
    incidents = active_data.get("incidents", [])
    print(f"  • Active incidents found: {len(incidents)}")
    assert len(incidents) >= 4, f"Expected at least 4 active incidents, got {len(incidents)}"

    print("\n  Current Active Incidents:")
    print("  " + "-" * 75)
    for inc in incidents:
        print(f"  [{inc['incident_id']}] {inc['temple']} - {inc['zone']} ({inc['density']}%) | Status: {inc['status']} | Risk: {inc['risk_level']}")
    print("  " + "-" * 75)

    target_inc_id = incidents[0]["incident_id"]

    # 3. Acknowledge First Incident
    print(f"\n[Step 3] Acknowledging incident {target_inc_id} via POST /api/incidents/{target_inc_id}/acknowledge...")
    status, ack_data = make_request("POST", f"/api/incidents/{target_inc_id}/acknowledge")
    assert status == 200, f"Expected 200, got {status}"
    assert ack_data["incident"]["status"] == "ACKNOWLEDGED", "Status should be ACKNOWLEDGED"
    assert ack_data["incident"]["acknowledged_at"] is not None, "acknowledged_at must be populated"
    print(f"  • Incident {target_inc_id} successfully marked ACKNOWLEDGED at {ack_data['incident']['acknowledged_at']}")

    # 4. Resolve First Incident
    print(f"\n[Step 4] Resolving incident {target_inc_id} via POST /api/incidents/{target_inc_id}/resolve...")
    status, res_data = make_request("POST", f"/api/incidents/{target_inc_id}/resolve")
    assert status == 200, f"Expected 200, got {status}"
    assert res_data["incident"]["status"] == "RESOLVED", "Status should be RESOLVED"
    assert res_data["incident"]["resolved_at"] is not None, "resolved_at must be populated"
    print(f"  • Incident {target_inc_id} successfully marked RESOLVED at {res_data['incident']['resolved_at']}")

    # 5. Verify Active Incidents Count Decreased
    print("\n[Step 5] Re-checking active incidents...")
    status, active_after = make_request("GET", "/api/incidents/active")
    assert status == 200
    active_ids = [i["incident_id"] for i in active_after.get("incidents", [])]
    assert target_inc_id not in active_ids, f"Resolved incident {target_inc_id} should no longer appear in active list"
    print(f"  • Active incidents count after resolution: {len(active_after.get('incidents', []))} (Resolved incident removed from active queue)")

    # 6. Verify History Audit Log
    print("\n[Step 6] Verifying history audit log via GET /api/incidents/history...")
    status, history_data = make_request("GET", "/api/incidents/history")
    assert status == 200
    history_incidents = history_data.get("incidents", [])
    resolved_in_history = next((i for i in history_incidents if i["incident_id"] == target_inc_id), None)
    assert resolved_in_history is not None, "Resolved incident must exist in history"
    assert resolved_in_history["status"] == "RESOLVED"
    print(f"  • Total historical incidents recorded: {len(history_incidents)}")
    print(f"  • Resolved incident {target_inc_id} confirmed in history audit log.")

    # 7. Error Handling: 404 for invalid incident ID
    print("\n[Step 7] Testing error handling for invalid incident ID...")
    status, err_data = make_request("POST", "/api/incidents/INVALID-ID-999/acknowledge")
    assert status == 404, f"Expected 404, got {status}"
    print(f"  • Non-existent incident rejected with HTTP 404: {err_data.get('detail')}")

    print("\n" + "=" * 80)
    print(">> ALL INCIDENT LIFECYCLE TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    test_incident_lifecycle()
