"""
Verification Test Script for Hackathon Demo Scenarios API.
"""

import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def test_demo_endpoint(name: str, path: str):
    url = f"{BASE_URL}{path}"
    print("\n" + "=" * 80)
    print(f">> TEST: {name}")
    print(f">> URL:  {url}")
    print("=" * 80)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"Status: {resp.status} OK")
            if "scenarios" in data:
                print(json.dumps(data, indent=2))
            else:
                score = data["intelligence"]["crowd_intelligence"]["final_crowd_score"]
                risk = data["intelligence"]["crowd_intelligence"]["final_risk_level"]
                trend = data["intelligence"]["crowd_intelligence"]["trend"]
                sec = data["resource_recommendations"]["security_personnel"]
                med = data["resource_recommendations"]["medical_personnel"]
                gates = data["resource_recommendations"]["additional_gates"]
                alert = data["resource_recommendations"]["emergency_team_alert"]
                prio = data["emergency_priority"]
                print(f"Temple: {data['temple']} | Score: {score}% | Risk: {risk} | Trend: {trend}")
                print(f"Security: {sec} units | Medical: {med} units | Gates: +{gates} | Alert: {alert} | Priority: {prio}")
                print(f"Queue Action: {data['operations']['queue_action']}")
                print(f"Parking Action: {data['operations']['parking_action']}")
                print(f"Priority Zones: {data['operations']['priority_zones']}")
                print(f"Active Alerts: {len(data['intelligence']['alerts'])}")
                print(f"Reasoning: {data['reasoning']}")
            return data
    except urllib.error.HTTPError as err:
        print(f"HTTP Error {err.code}: {err.read().decode('utf-8')}")
        return None
    except Exception as err:
        print(f"Error: {err}")
        return None


if __name__ == "__main__":
    # 1. Scenarios List
    test_demo_endpoint("1. List Demo Scenarios", "/api/demo/scenarios")

    # 2. Normal Day
    test_demo_endpoint("2. Demo: Normal Day (LOW)", "/api/demo/normal-day")

    # 3. Busy Weekend
    test_demo_endpoint("3. Demo: Busy Weekend (MODERATE)", "/api/demo/busy-weekend")

    # 4. Festival Rush
    test_demo_endpoint("4. Demo: Festival Rush (HIGH)", "/api/demo/festival-rush")

    # 5. Emergency Overcrowding
    test_demo_endpoint("5. Demo: Emergency Overcrowding (CRITICAL)", "/api/demo/emergency-overcrowding")

    # 6. Error handling
    test_demo_endpoint("6. Demo: Invalid Scenario (404 Error Handling)", "/api/demo/unknown-scenario")
