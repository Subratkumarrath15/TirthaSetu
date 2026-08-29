"""
Hackathon Demo Scenario System for YatraSafe AI + Real-Time Intelligence Module.

Provides deterministic, reproducible operational scenarios covering the complete
safety lifecycle (LOW -> MODERATE -> HIGH -> CRITICAL) for the 4 Gujarat pilgrimage sites:
- Somnath (Normal Day -> LOW)
- Dwarka (Busy Weekend -> MODERATE)
- Ambaji (Festival Rush -> HIGH)
- Pavagadh (Emergency Overcrowding -> CRITICAL)
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

from crowd_engine.crowd_engine import (
    INTELLIGENCE_ACTIONS,
    calculate_final_risk_level,
    determine_crowd_trend,
)
from ml.predict import predict_crowd
from resource_engine.resource_recommender import recommend_resources

# 4 Controlled Hackathon Demo Scenarios demonstrating LOW -> MODERATE -> HIGH -> CRITICAL
DEMO_SCENARIOS = {
    "normal-day": {
        "slug": "normal-day",
        "title": "Scenario 1: Normal Day Operations",
        "description": "Routine weekday operations at Somnath with smooth queue movement, low footfall, and green safety status.",
        "temple": "Somnath",
        "context": {
            "hour": 10,
            "day_of_week": "Wednesday",
            "is_weekend": 0,
            "is_holiday": 0,
            "is_festival": 0,
            "weather": "Clear",
            "temperature": 28.0,
            "previous_visitors": 500,
        },
        "zones": [
            {"zone": "Main Gate", "capacity": 3500, "current_people": 770, "inflow": 8, "outflow": 8},
            {"zone": "Darshan Queue", "capacity": 10000, "current_people": 2200, "inflow": 12, "outflow": 12},
            {"zone": "Temple Entrance", "capacity": 3000, "current_people": 660, "inflow": 7, "outflow": 7},
            {"zone": "Parking", "capacity": 2500, "current_people": 550, "inflow": 4, "outflow": 4},
        ],
    },
    "busy-weekend": {
        "slug": "busy-weekend",
        "title": "Scenario 2: Busy Weekend Darshan",
        "description": "Saturday morning pilgrim influx at Dwarkadhish Temple with increased queue buildup, elevated density, and yellow moderate alert.",
        "temple": "Dwarka",
        "context": {
            "hour": 8,
            "day_of_week": "Saturday",
            "is_weekend": 1,
            "is_holiday": 0,
            "is_festival": 0,
            "weather": "Clear",
            "temperature": 27.0,
            "previous_visitors": 800,
        },
        "zones": [
            {"zone": "Main Gate", "capacity": 3000, "current_people": 1650, "inflow": 25, "outflow": 20},
            {"zone": "Darshan Queue", "capacity": 9000, "current_people": 5400, "inflow": 35, "outflow": 28},
            {"zone": "Temple Entrance", "capacity": 2500, "current_people": 1375, "inflow": 20, "outflow": 16},
            {"zone": "Parking", "capacity": 2000, "current_people": 1100, "inflow": 12, "outflow": 8},
        ],
    },
    "festival-rush": {
        "slug": "festival-rush",
        "title": "Scenario 3: Major Festival Surge",
        "description": "High-volume festival evening at Ambaji Shakti Peeth requiring active queue rerouting, barrier deployment, and orange high alert.",
        "temple": "Ambaji",
        "context": {
            "hour": 18,
            "day_of_week": "Sunday",
            "is_weekend": 1,
            "is_holiday": 1,
            "is_festival": 1,
            "weather": "Sunny",
            "temperature": 31.0,
            "previous_visitors": 4500,
        },
        "zones": [
            {"zone": "Main Gate", "capacity": 4500, "current_people": 3375, "inflow": 45, "outflow": 32},
            {"zone": "Darshan Queue", "capacity": 14000, "current_people": 11200, "inflow": 60, "outflow": 40},
            {"zone": "Temple Entrance", "capacity": 4000, "current_people": 3000, "inflow": 32, "outflow": 22},
            {"zone": "Parking", "capacity": 3000, "current_people": 2250, "inflow": 20, "outflow": 12},
        ],
    },
    "emergency-overcrowding": {
        "slug": "emergency-overcrowding",
        "title": "Scenario 4: Critical Overcrowding & Emergency Alert",
        "description": "Severe bottleneck surge at Pavagadh Mahakali temple exceeding critical thresholds (density >90%, parking 90%), triggering emergency teams and red critical alert.",
        "temple": "Pavagadh",
        "context": {
            "hour": 17,
            "day_of_week": "Sunday",
            "is_weekend": 1,
            "is_holiday": 0,
            "is_festival": 1,
            "weather": "Clear",
            "temperature": 29.0,
            "previous_visitors": 2100,
            "current_crowd": 7000,
        },
        "zones": [
            {"zone": "Main Gate", "capacity": 2000, "current_people": 1840, "inflow": 95, "outflow": 50},
            {"zone": "Darshan Queue", "capacity": 6000, "current_people": 5700, "inflow": 120, "outflow": 60},
            {"zone": "Temple Entrance", "capacity": 1800, "current_people": 1692, "inflow": 75, "outflow": 35},
            {"zone": "Parking", "capacity": 1200, "current_people": 1080, "inflow": 40, "outflow": 10},
        ],
    },
}


def run_demo_scenario(scenario_name: str) -> dict:
    """
    Execute a controlled hackathon demo scenario through the real AI & Resource pipeline.

    Parameters:
        scenario_name (str): One of 'normal-day', 'busy-weekend', 'festival-rush', 'emergency-overcrowding'.

    Returns:
        dict: Standardized full-status report identical to /api/full-status/{temple}.
    """
    normalized_key = scenario_name.strip().lower().replace("_", "-")
    if normalized_key not in DEMO_SCENARIOS:
        raise ValueError(
            f"Unknown demo scenario '{scenario_name}'. Supported scenarios: {list(DEMO_SCENARIOS.keys())}"
        )

    scenario_cfg = DEMO_SCENARIOS[normalized_key]
    temple = scenario_cfg["temple"]
    ctx = scenario_cfg["context"]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Build Controlled Multi-Zone Telemetry Snapshot
    zone_records = []
    total_current_people = 0
    densities = []
    parking_occupancy = 0.0

    for z in scenario_cfg["zones"]:
        z_name = z["zone"]
        capacity = z["capacity"]
        current = z["current_people"]
        density_pct = round(min(100.0, (current / capacity) * 100.0), 2)
        densities.append(density_pct)

        if z_name == "Parking":
            parking_occupancy = density_pct
            parking_occ_field = density_pct
        else:
            total_current_people += current
            parking_occ_field = None

        if density_pct < 40.0:
            risk_tier = "LOW"
        elif density_pct < 70.0:
            risk_tier = "MODERATE"
        elif density_pct < 85.0:
            risk_tier = "HIGH"
        else:
            risk_tier = "CRITICAL"

        zone_records.append({
            "temple": temple,
            "zone": z_name,
            "people_entering": z["inflow"],
            "people_exiting": z["outflow"],
            "current_people": current,
            "crowd_density": density_pct,
            "parking_occupancy": parking_occ_field,
            "risk_level": risk_tier,
            "timestamp": now_str,
        })

    average_live_density = round(sum(densities) / len(densities), 2)
    max_zone_density = max(densities)
    highest_risk_record = max(zone_records, key=lambda r: r["crowd_density"])
    highest_risk_zone = highest_risk_record["zone"]

    # 2. Invoke Existing AI Prediction Engine (ml/predict.py)
    ai_result = predict_crowd(
        temple=temple,
        hour=ctx["hour"],
        day_of_week=ctx["day_of_week"],
        is_weekend=ctx["is_weekend"],
        is_holiday=ctx["is_holiday"],
        is_festival=ctx["is_festival"],
        weather=ctx["weather"],
        temperature=ctx["temperature"],
        previous_visitors=ctx["previous_visitors"],
        current_crowd=ctx.get("current_crowd", total_current_people),
    )

    ai_predicted_visitors = ai_result["predicted_visitors"]
    temple_capacity = ai_result["temple_capacity"]

    # In operational crowd forecasting, hourly inflow saturation is evaluated against peak hourly capacity
    # (~15% of total 24hr complex capacity) to accurately trigger operational surge risk.
    peak_hourly_capacity = temple_capacity * 0.15
    ai_crowd_percentage = round(min(100.0, max(0.0, (ai_predicted_visitors / peak_hourly_capacity) * 100.0)), 2)

    if ai_crowd_percentage < 40.0:
        ai_risk_level = "LOW"
    elif ai_crowd_percentage < 70.0:
        ai_risk_level = "MODERATE"
    elif ai_crowd_percentage < 85.0:
        ai_risk_level = "HIGH"
    else:
        ai_risk_level = "CRITICAL"

    # 3. Compute Unified Crowd Score (40% AI Forecast + 60% Live Telemetry)
    # Formula: final_crowd_score = (0.40 * ai_crowd_percentage) + (0.60 * average_live_density)
    raw_final_score = (0.40 * ai_crowd_percentage) + (0.60 * average_live_density)
    final_crowd_score = round(min(100.0, max(0.0, raw_final_score)), 2)
    final_risk_level = calculate_final_risk_level(final_crowd_score)
    trend = determine_crowd_trend(average_live_density, ai_crowd_percentage)
    recommended_action = INTELLIGENCE_ACTIONS[final_risk_level]

    # 4. Generate Critical Individual Zone Alerts (Density >= 85%)
    alerts = []
    for z in zone_records:
        if z["crowd_density"] >= 85.0:
            alerts.append({
                "temple": temple,
                "zone": z["zone"],
                "zone_density": z["crowd_density"],
                "risk_level": "CRITICAL",
                "recommended_immediate_action": (
                    f"Immediate queue relief required at {z['zone']}. "
                    "Halt upstream inflow, open emergency bypass gates, and dispatch marshals."
                ),
            })

    # 5. Assemble Intelligence Object for Resource Recommender
    intelligence_payload = {
        "temple": temple,
        "timestamp": now_str,
        "ai_prediction": {
            "predicted_visitors": ai_predicted_visitors,
            "crowd_percentage": ai_crowd_percentage,
            "risk_level": ai_risk_level,
        },
        "live_data": {
            "average_density": average_live_density,
            "max_zone_density": max_zone_density,
            "total_current_people": total_current_people,
            "highest_risk_zone": highest_risk_zone,
            "parking_occupancy": parking_occupancy,
            "zones": zone_records,
        },
        "crowd_intelligence": {
            "final_crowd_score": final_crowd_score,
            "final_risk_level": final_risk_level,
            "trend": trend,
            "recommended_action": recommended_action,
        },
        "alerts": alerts,
    }

    # 6. Invoke Existing Resource Recommendation Engine (resource_engine/resource_recommender.py)
    resource_result = recommend_resources(intelligence_payload)

    # 7. Return Clean Master Payload matching /api/full-status/{temple}
    return {
        "temple": temple,
        "timestamp": now_str,
        "zones": zone_records,
        "intelligence": {
            "ai_prediction": intelligence_payload["ai_prediction"],
            "live_data": intelligence_payload["live_data"],
            "crowd_intelligence": intelligence_payload["crowd_intelligence"],
            "alerts": intelligence_payload["alerts"],
        },
        "resource_recommendations": resource_result["resource_recommendations"],
        "operations": resource_result["operations"],
        "emergency_priority": resource_result["emergency_priority"],
        "reasoning": resource_result["reasoning"],
    }


def run_all_scenarios():
    """Execute and display all 4 demo scenarios in a formatted progression table."""
    print("=" * 115)
    print(">> YATRASAFE GUJARAT HACKATHON DEMO PROGRESSION: LOW -> MODERATE -> HIGH -> CRITICAL")
    print("=" * 115)

    headers = [
        ("SCENARIO", 24),
        ("TEMPLE", 13),
        ("CROWD SCORE", 13),
        ("RISK LEVEL", 12),
        ("TREND", 10),
        ("SECURITY", 10),
        ("MEDICAL", 9),
        ("GATES", 7),
        ("PRIORITY", 10),
    ]

    header_line = " | ".join(f"{title:<{width}}" for title, width in headers)
    print(header_line)
    print("-" * 115)

    results = []
    for slug, cfg in DEMO_SCENARIOS.items():
        res = run_demo_scenario(slug)
        results.append((slug, res))

        sc_title = cfg["title"].split(":")[0] + f" ({slug})"
        temple = res["temple"]
        score = f"{res['intelligence']['crowd_intelligence']['final_crowd_score']:.1f}%"
        risk = res["intelligence"]["crowd_intelligence"]["final_risk_level"]
        trend = res["intelligence"]["crowd_intelligence"]["trend"]
        sec = f"{res['resource_recommendations']['security_personnel']} units"
        med = f"{res['resource_recommendations']['medical_personnel']} units"
        gates = f"+{res['resource_recommendations']['additional_gates']}"
        prio = res["emergency_priority"]

        row = [
            (sc_title, 24),
            (temple, 13),
            (score, 13),
            (risk, 12),
            (trend, 10),
            (sec, 10),
            (med, 9),
            (gates, 7),
            (prio, 10),
        ]
        print(" | ".join(f"{val:<{width}}" for val, width in row))

    print("=" * 115)
    return results


if __name__ == "__main__":
    run_all_scenarios()
