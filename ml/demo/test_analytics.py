"""
Verification and Test Suite for YatraSafe Analytics & Decision Insights Engine (4 Gujarat Shrines).
"""

import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def make_request(path: str):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def test_analytics_endpoints():
    print("=" * 80)
    print(">> TESTING YATRASAFE ANALYTICS & DECISION INSIGHTS ENGINE")
    print("=" * 80)

    # 1. Test Summary Endpoint
    print("\n[Test 1] Testing GET /api/analytics/summary...")
    status, summary = make_request("/api/analytics/summary")
    assert status == 200, f"Expected 200, got {status}"
    print(f"  • Average Crowd Score: {summary['average_crowd_score']}%")
    print(f"  • Highest-Risk Temple: {summary['highest_risk_temple']} ({summary['highest_risk_level']})")
    print(f"  • Critical Bottleneck Zone: {summary['most_affected_zone']}")
    print(f"  • Incident Summary: {summary['incident_summary']}")
    print(f"  • Risk Distribution Counts: {summary['risk_level_distribution']}")
    print(f"  • Operational Insight: {summary['operational_insight']}")
    assert "average_crowd_score" in summary
    assert "highest_risk_temple" in summary
    assert "operational_insight" in summary
    print("  >> GET /api/analytics/summary PASSED!")

    # 2. Test Trends Endpoint
    print("\n[Test 2] Testing GET /api/analytics/trends...")
    status, trends = make_request("/api/analytics/trends?limit=10")
    assert status == 200, f"Expected 200, got {status}"
    assert "series" in trends
    print(f"  • Total historical snapshot points: {trends['total_points']}")
    for s in trends["series"][:3]:
        print(f"    - [{s['timestamp']}] {s['temple']}: Score {s['crowd_score']}% ({s['risk_level']})")
    print("  >> GET /api/analytics/trends PASSED!")

    # 3. Test Risk Distribution Endpoint
    print("\n[Test 3] Testing GET /api/analytics/risk-distribution...")
    status, dist = make_request("/api/analytics/risk-distribution")
    assert status == 200, f"Expected 200, got {status}"
    assert "percentages" in dist
    print(f"  • Breakdown Percentages: {dist['percentages']}")
    print("  >> GET /api/analytics/risk-distribution PASSED!")

    # 4. Test Temple Comparison Endpoint
    print("\n[Test 4] Testing GET /api/analytics/temple-comparison...")
    status, comp = make_request("/api/analytics/temple-comparison")
    assert status == 200, f"Expected 200, got {status}"
    assert "comparison" in comp
    assert comp["total_temples"] == 4, f"Expected 4 temples, got {comp['total_temples']}"
    print(f"  • Compared Temples ({comp['total_temples']}):")
    for t in comp["comparison"]:
        print(f"    - {t['temple']:12} | Latest: {t['latest_crowd_score']:5.1f}% | Risk: {t['risk_level']:8} | Max Zone: {t['max_zone_density']:5.1f}% | Active Alerts: {t['active_incidents']}")
    print("  >> GET /api/analytics/temple-comparison PASSED!")

    # 5. Test Incident Analytics Endpoint
    print("\n[Test 5] Testing GET /api/analytics/incidents...")
    status, inc_analytics = make_request("/api/analytics/incidents")
    assert status == 200, f"Expected 200, got {status}"
    assert "breakdown_by_risk" in inc_analytics
    print(f"  • Total Incidents Logged: {inc_analytics['total_incidents']}")
    print(f"  • Active Incidents: {inc_analytics['active_incidents']}")
    print(f"  • Resolved Incidents: {inc_analytics['resolved_incidents']}")
    print(f"  • Breakdown by Risk: {inc_analytics['breakdown_by_risk']}")
    print("  >> GET /api/analytics/incidents PASSED!")

    # 6. Test Triggering a Demo Scenario Updates Analytics
    print("\n[Test 6] Testing Analytics live snapshot recording via Demo Scenario...")
    status, demo_res = make_request("/api/demo/emergency-overcrowding")
    assert status == 200
    status, updated_trends = make_request("/api/analytics/trends?limit=5")
    latest_snapshot = updated_trends["series"][-1]
    print(f"  • Latest Snapshot recorded: {latest_snapshot['temple']} ({latest_snapshot['crowd_score']}%)")
    assert latest_snapshot["temple"] == "Pavagadh", f"Expected Pavagadh, got {latest_snapshot['temple']}"
    print("  >> Live snapshot recording on demo execution PASSED!")

    print("\n" + "=" * 80)
    print(">> ALL 6 ANALYTICS & DECISION INSIGHTS TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    test_analytics_endpoints()
