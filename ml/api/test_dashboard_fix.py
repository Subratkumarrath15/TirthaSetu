"""
Verification Test for Government Dashboard Scenario Consistency Fix (4 Gujarat Shrines).
"""

import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def test_scenario_zones(slug: str, expected_temple: str, expected_densities: dict):
    url = f"{BASE_URL}/api/demo/{slug}"
    print("\n" + "=" * 80)
    print(f">> TESTING SCENARIO: {slug.upper()}")
    print(f">> URL: {url}")
    print("=" * 80)

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

        temple = data["temple"]
        score = data["intelligence"]["crowd_intelligence"]["final_crowd_score"]
        risk = data["intelligence"]["crowd_intelligence"]["final_risk_level"]
        zones = data.get("zones", [])

        print(f"Status: {resp.status} OK | Temple: {temple} | Crowd Score: {score}% | Risk: {risk}")
        assert temple == expected_temple, f"Expected temple {expected_temple}, got {temple}"
        assert len(zones) == 4, f"Expected 4 zones, got {len(zones)}"

        print("-" * 80)
        print(f"{'ZONE NAME':<20} | {'DENSITY':<10} | {'RISK LEVEL':<12} | {'PEOPLE':<10} | {'INFLOW/OUTFLOW'}")
        print("-" * 80)

        for z in zones:
            z_name = z["zone"]
            density = z["crowd_density"]
            z_risk = z["risk_level"]
            people = z["current_people"]
            flow = f"+{z['people_entering']} / -{z['people_exiting']}"
            print(f"{z_name:<20} | {density:5.1f}%    | {z_risk:<12} | {people:<10} | {flow}")

            if z_name in expected_densities:
                expected_d = expected_densities[z_name]
                assert abs(density - expected_d) < 0.1, f"Expected {expected_d}% for {z_name}, got {density}%"

        print(">> Zone verification: ALL 4 ZONES MATCH EXPECTED VALUES!")
        return data


def test_live_full_status():
    url = f"{BASE_URL}/api/full-status/Somnath?hour=10&day_of_week=Thursday&is_weekend=0&is_holiday=0&is_festival=0&weather=Sunny&temperature=30&previous_visitors=4500"
    print("\n" + "=" * 80)
    print(">> TESTING LIVE FULL STATUS (Somnath)")
    print(f">> URL: {url}")
    print("=" * 80)

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        zones = data.get("zones", [])
        print(f"Status: {resp.status} OK | Temple: {data['temple']} | Live zones count: {len(zones)}")
        assert len(zones) == 4, f"Expected 4 live zones, got {len(zones)}"
        for z in zones:
            print(f"  • {z['zone']}: {z['crowd_density']}% ({z['risk_level']}) - {z['current_people']} people")
        print(">> Live full-status verification: PASSED!")


if __name__ == "__main__":
    # 1. Normal Day
    test_scenario_zones(
        "normal-day",
        "Somnath",
        {"Main Gate": 22.0, "Darshan Queue": 22.0, "Temple Entrance": 22.0, "Parking": 22.0},
    )

    # 2. Busy Weekend
    test_scenario_zones(
        "busy-weekend",
        "Dwarka",
        {"Main Gate": 55.0, "Darshan Queue": 60.0, "Temple Entrance": 55.0, "Parking": 55.0},
    )

    # 3. Festival Rush
    test_scenario_zones(
        "festival-rush",
        "Ambaji",
        {"Main Gate": 75.0, "Darshan Queue": 80.0, "Temple Entrance": 75.0, "Parking": 75.0},
    )

    # 4. Emergency Overcrowding (Exact requirements: 92%, 95%, 94%, 90%)
    test_scenario_zones(
        "emergency-overcrowding",
        "Pavagadh",
        {"Main Gate": 92.0, "Darshan Queue": 95.0, "Temple Entrance": 94.0, "Parking": 90.0},
    )

    # 5. Live Full Status
    test_live_full_status()

    print("\n" + "=" * 80)
    print(">> ALL DEMO SCENARIO ZONES & LIVE FEEDS SUCCESSFULLY VALIDATED!")
    print("=" * 80)
