"""
Smart Resource Recommendation Engine for YatraSafe AI + Real-Time Module.

Transforms fused crowd intelligence diagnostics and real-time telemetry metrics
into actionable operational resource allocations (security personnel, medical units,
gate management, queue protocols, and parking routing).
"""

import json
import os
import sys
from datetime import datetime

# Ensure project root is available in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crowd_engine.crowd_engine import analyze_temple

# Baseline resource configurations mapped to fused risk tiers
BASE_RESOURCE_POLICIES = {
    "LOW": {
        "security_personnel": 2,
        "medical_personnel": 1,
        "additional_gates": 0,
        "queue_action": "Normal queue operations",
        "emergency_priority": "LOW",
    },
    "MODERATE": {
        "security_personnel": 4,
        "medical_personnel": 1,
        "additional_gates": 1,
        "queue_action": "Increase monitoring and prepare alternate queue routing",
        "emergency_priority": "MODERATE",
    },
    "HIGH": {
        "security_personnel": 8,
        "medical_personnel": 2,
        "additional_gates": 2,
        "queue_action": "Activate alternate queue routing and deploy crowd control barriers",
        "emergency_priority": "HIGH",
    },
    "CRITICAL": {
        "security_personnel": 15,
        "medical_personnel": 4,
        "additional_gates": 3,
        "queue_action": "Restrict incoming flow and immediately redirect pilgrims to alternate routes",
        "emergency_priority": "CRITICAL",
    },
}


def recommend_resources(intelligence_result: dict) -> dict:
    """
    Generate dynamic operational resource recommendations from crowd intelligence diagnostics.

    Parameters:
        intelligence_result (dict): Output payload from crowd_engine.analyze_temple().

    Returns:
        dict: Standardized operational resource allocation report.
    """
    # 1. Input Validation
    if not isinstance(intelligence_result, dict):
        raise ValueError("Invalid intelligence_result: expected a dictionary.")

    temple = intelligence_result.get("temple")
    if not temple:
        raise ValueError("Missing 'temple' field in intelligence_result.")

    timestamp = intelligence_result.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    crowd_intel = intelligence_result.get("crowd_intelligence")
    if not isinstance(crowd_intel, dict):
        raise ValueError("Missing or invalid 'crowd_intelligence' sub-object in intelligence_result.")

    live_data = intelligence_result.get("live_data")
    if not isinstance(live_data, dict):
        raise ValueError("Missing or invalid 'live_data' sub-object in intelligence_result.")

    alerts = intelligence_result.get("alerts", [])
    if not isinstance(alerts, list):
        alerts = []

    # 2. Extract Key Diagnostic Metrics
    final_crowd_score = float(crowd_intel.get("final_crowd_score", 0.0))
    final_risk_level = str(crowd_intel.get("final_risk_level", "LOW")).upper()
    trend = str(crowd_intel.get("trend", "STABLE")).upper()

    max_zone_density = float(live_data.get("max_zone_density", 0.0))
    highest_risk_zone = str(live_data.get("highest_risk_zone", "Unknown"))
    total_current_people = int(live_data.get("total_current_people", 0))
    parking_occupancy = float(live_data.get("parking_occupancy", 0.0))

    if final_risk_level not in BASE_RESOURCE_POLICIES:
        final_risk_level = "LOW"

    # 3. Initialize Baseline Allocations
    policy = BASE_RESOURCE_POLICIES[final_risk_level]
    security_personnel = policy["security_personnel"]
    medical_personnel = policy["medical_personnel"]
    additional_gates = policy["additional_gates"]
    queue_action = policy["queue_action"]
    emergency_priority = policy["emergency_priority"]

    parking_action = "Normal parking operations. Sufficient capacity available."
    zone_intervention_required = False
    emergency_team_alert = False
    priority_zones = []
    reasoning = [f"Base allocation established for {final_risk_level} risk tier (Crowd Score: {final_crowd_score:.2f}%)."]

    # 4. Dynamic Adjustment 1: RISING Trend
    if trend == "RISING":
        security_personnel += 2
        reasoning.append("Trend is RISING: Allocated +2 security personnel for proactive inflow containment.")

    # 5. Dynamic Adjustment 2: High Zone Density (>= 85%)
    if max_zone_density >= 85.0:
        security_personnel += 3
        zone_intervention_required = True
        reasoning.append(
            f"Critical saturation in {highest_risk_zone} ({max_zone_density:.1f}% density): "
            "Allocated +3 security personnel and enabled mandatory zone intervention."
        )

    # 6. Dynamic Adjustment 3: High Parking Occupancy (>= 85%)
    if parking_occupancy >= 85.0:
        parking_action = "Redirect incoming vehicles to alternate parking."
        reasoning.append(
            f"Parking capacity critical ({parking_occupancy:.1f}% occupancy): "
            "Vehicle diversion protocol activated."
        )

    # 7. Dynamic Adjustment 4: Emergency Team Alert (HIGH or CRITICAL)
    if final_risk_level in ["HIGH", "CRITICAL"]:
        emergency_team_alert = True
        reasoning.append(
            f"Risk level is {final_risk_level}: Emergency and medical response teams placed on active standby."
        )

    # 8. Dynamic Adjustment 5: Priority Active Zone Alerts
    if alerts:
        extracted_zones = [
            a.get("zone") for a in alerts if isinstance(a, dict) and a.get("zone")
        ]
        priority_zones = list(dict.fromkeys(extracted_zones))
        if priority_zones:
            reasoning.append(
                f"Active critical alerts triggered for priority zones: {', '.join(priority_zones)}."
            )
    elif max_zone_density >= 85.0 and highest_risk_zone != "Unknown":
        priority_zones = [highest_risk_zone]

    # 9. Assemble Standardized Response Payload
    return {
        "temple": temple,
        "timestamp": timestamp,
        "resource_recommendations": {
            "security_personnel": security_personnel,
            "medical_personnel": medical_personnel,
            "additional_gates": additional_gates,
            "emergency_team_alert": emergency_team_alert,
        },
        "operations": {
            "queue_action": queue_action,
            "parking_action": parking_action,
            "zone_intervention_required": zone_intervention_required,
            "priority_zones": priority_zones,
        },
        "emergency_priority": emergency_priority,
        "reasoning": reasoning,
    }


if __name__ == "__main__":
    print("=" * 80)
    print(">> YATRASAFE SMART RESOURCE RECOMMENDATION ENGINE TEST SUITE")
    print("=" * 80)

    # Scenario 1: Normal Weekday Scenario (Somnath)
    print("\n--- TEST SCENARIO 1: Somnath Normal Weekday ---")
    intel_1 = analyze_temple(
        temple="Somnath",
        hour=10,
        day_of_week="Wednesday",
        is_weekend=0,
        is_holiday=0,
        is_festival=0,
        weather="Clear",
        temperature=28.0,
        previous_visitors=750,
    )
    rec_1 = recommend_resources(intel_1)
    print(json.dumps(rec_1, indent=4))

    # Scenario 2: Busy Weekend Scenario (Dwarka)
    print("\n--- TEST SCENARIO 2: Dwarka Busy Weekend Darshan ---")
    intel_2 = analyze_temple(
        temple="Dwarka",
        hour=8,
        day_of_week="Saturday",
        is_weekend=1,
        is_holiday=0,
        is_festival=0,
        weather="Clear",
        temperature=30.0,
        previous_visitors=2200,
    )
    rec_2 = recommend_resources(intel_2)
    print(json.dumps(rec_2, indent=4))

    # Scenario 3: Festival / Critical Saturation Scenario (Pavagadh Festival)
    print("\n--- TEST SCENARIO 3: Pavagadh Major Festival / Critical Scenario ---")
    intel_3 = analyze_temple(
        temple="Pavagadh",
        hour=18,
        day_of_week="Sunday",
        is_weekend=1,
        is_holiday=1,
        is_festival=1,
        weather="Sunny",
        temperature=31.0,
        previous_visitors=4500,
    )
    # Inject synthetic critical zone and parking conditions to verify dynamic threshold escalations
    intel_3_high_risk = dict(intel_3)
    intel_3_high_risk["crowd_intelligence"] = {
        "final_crowd_score": 86.5,
        "final_risk_level": "CRITICAL",
        "trend": "RISING",
        "recommended_action": "Open additional gates and alert emergency response teams.",
    }
    intel_3_high_risk["live_data"] = {
        "average_density": 88.2,
        "max_zone_density": 95.0,
        "total_current_people": 18200,
        "highest_risk_zone": "Darshan Queue",
        "parking_occupancy": 90.0,
    }
    intel_3_high_risk["alerts"] = [
        {
            "temple": "Pavagadh",
            "zone": "Darshan Queue",
            "zone_density": 95.0,
            "risk_level": "CRITICAL",
            "recommended_immediate_action": "Immediate queue relief required.",
        }
    ]

    rec_3 = recommend_resources(intel_3_high_risk)
    print(json.dumps(rec_3, indent=4))

    print("\n" + "=" * 80)
    print(">> All Resource Recommendation test scenarios executed successfully.")
    print("=" * 80)
