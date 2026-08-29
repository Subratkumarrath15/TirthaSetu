"""
Crowd Intelligence Engine for YatraSafe AI + Real-Time Module.

Fuses trained Machine Learning predictive intelligence (40% weight) with
live IoT multi-zone sensor telemetry (60% weight) to produce unified crowd safety scores,
directional crowd trends, zone saturation alerts, and operational response directives.
"""

import json
import os
import sys
from datetime import datetime

# Ensure project root is in sys.path for direct script execution and package imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.predict import (
    SUPPORTED_TEMPLES,
    TEMPLE_CAPACITIES,
    predict_crowd,
)

# Smart operational recommendation directives based on fused risk levels
INTELLIGENCE_ACTIONS = {
    "LOW": "Normal operations. Continue routine monitoring.",
    "MODERATE": "Increase monitoring and prepare additional queue and security resources.",
    "HIGH": "Deploy additional security staff, activate alternate queue routing, and closely monitor high-density zones.",
    "CRITICAL": "Open additional gates, restrict incoming flow if necessary, redirect pilgrims, deploy emergency and medical teams, and immediately address the highest-risk zone.",
}

# Trend Sensitivity Threshold:
# If live sensor crowd density deviates from AI predicted crowd percentage by >= 5.0%,
# the crowd flow is classified as RISING or FALLING; otherwise it is STABLE.
TREND_DELTA_THRESHOLD = 5.0


def calculate_final_risk_level(final_score: float) -> str:
    """Classify combined crowd intelligence score into standard risk tiers."""
    if final_score < 40.0:
        return "LOW"
    elif final_score < 70.0:
        return "MODERATE"
    elif final_score < 85.0:
        return "HIGH"
    else:
        return "CRITICAL"


def determine_crowd_trend(live_density: float, ai_percentage: float) -> str:
    """
    Compute real-time crowd dynamics trend.

    Logic:
    - RISING: Live density exceeds predictive expectation by >= TREND_DELTA_THRESHOLD (surge/bottleneck)
    - FALLING: Live density drops below predictive expectation by >= TREND_DELTA_THRESHOLD (dispersal)
    - STABLE: Live telemetry aligns within +/- TREND_DELTA_THRESHOLD of predicted levels
    """
    delta = live_density - ai_percentage
    if delta >= TREND_DELTA_THRESHOLD:
        return "RISING"
    elif delta <= -TREND_DELTA_THRESHOLD:
        return "FALLING"
    else:
        return "STABLE"


def load_live_sensor_data(sensor_data_path: str = None) -> dict:
    """Load latest sensor snapshot from disk with error validation."""
    if sensor_data_path is None:
        sensor_data_path = os.path.join(PROJECT_ROOT, "realtime", "latest_sensor_data.json")

    if not os.path.exists(sensor_data_path):
        raise FileNotFoundError(
            f"Sensor telemetry snapshot not found at '{sensor_data_path}'. "
            "Please run realtime/sensor_simulator.py to generate live sensor feeds."
        )

    try:
        with open(sensor_data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse sensor snapshot JSON: {exc}")


def analyze_temple(
    temple: str,
    hour: int,
    day_of_week: str,
    is_weekend: int,
    is_holiday: int,
    is_festival: int,
    weather: str,
    temperature: float,
    previous_visitors: int,
    sensor_data_path: str = None,
) -> dict:
    """
    Perform unified crowd intelligence analysis combining AI prediction and live sensor telemetry.

    Parameters:
        temple (str): Target temple name.
        hour (int): Hour of day (0 - 23).
        day_of_week (str): Day of week string.
        is_weekend (int): 1 if weekend, else 0.
        is_holiday (int): 1 if holiday, else 0.
        is_festival (int): 1 if festival, else 0.
        weather (str): Weather condition string.
        temperature (float): Current temperature in Celsius.
        previous_visitors (int): Previous hour inflow count.
        sensor_data_path (str, optional): Custom path to latest_sensor_data.json.

    Returns:
        dict: Complete unified crowd intelligence diagnostic report.
    """
    # 1. Validate Temple
    if temple not in SUPPORTED_TEMPLES:
        raise ValueError(
            f"Unsupported temple '{temple}'. Supported temples are: {SUPPORTED_TEMPLES}"
        )

    # 2. Ingest Live Sensor Telemetry
    sensor_snapshot = load_live_sensor_data(sensor_data_path)
    sensors_list = sensor_snapshot.get("sensors", [])

    # Filter zones for requested temple
    temple_zones = [s for s in sensors_list if s.get("temple") == temple]
    if not temple_zones:
        raise ValueError(
            f"No live sensor telemetry found for temple '{temple}' in the current sensor snapshot."
        )

    # 3. Aggregate Live Metrics
    non_parking_zones = [z for z in temple_zones if z.get("zone") != "Parking"]
    parking_zone = next((z for z in temple_zones if z.get("zone") == "Parking"), None)

    # Calculate live aggregates
    all_densities = [float(z.get("crowd_density", 0.0)) for z in temple_zones]
    average_live_density = round(sum(all_densities) / len(all_densities), 2) if all_densities else 0.0

    max_zone_record = max(temple_zones, key=lambda z: float(z.get("crowd_density", 0.0)))
    max_zone_density = round(float(max_zone_record.get("crowd_density", 0.0)), 2)
    highest_risk_zone = max_zone_record.get("zone", "Unknown")

    total_current_people = sum(int(z.get("current_people", 0)) for z in non_parking_zones)
    parking_occupancy = round(float(parking_zone.get("parking_occupancy", 0.0)), 2) if parking_zone and parking_zone.get("parking_occupancy") is not None else 0.0

    # 4. Invoke AI Prediction Engine with Live Population as current_crowd
    ai_result = predict_crowd(
        temple=temple,
        hour=hour,
        day_of_week=day_of_week,
        is_weekend=is_weekend,
        is_holiday=is_holiday,
        is_festival=is_festival,
        weather=weather,
        temperature=temperature,
        previous_visitors=previous_visitors,
        current_crowd=total_current_people,
    )

    ai_predicted_visitors = ai_result["predicted_visitors"]
    ai_crowd_percentage = float(ai_result["crowd_percentage"])
    ai_risk_level = ai_result["risk_level"]

    # 5. Calculate Unified Crowd Score (40% AI Forecast + 60% Live Telemetry)
    # Formula: final_crowd_score = (0.40 * ai_crowd_percentage) + (0.60 * average_live_density)
    raw_final_score = (0.40 * ai_crowd_percentage) + (0.60 * average_live_density)
    final_crowd_score = round(min(100.0, max(0.0, raw_final_score)), 2)

    # 6. Determine Fused Risk Level & Trend
    final_risk_level = calculate_final_risk_level(final_crowd_score)
    trend = determine_crowd_trend(average_live_density, ai_crowd_percentage)
    recommended_action = INTELLIGENCE_ACTIONS[final_risk_level]

    # 7. Generate Critical Individual Zone Alerts (Density >= 85%)
    alerts = []
    for z in temple_zones:
        zone_name = z.get("zone")
        zone_density = round(float(z.get("crowd_density", 0.0)), 2)
        if zone_density >= 85.0:
            alerts.append({
                "temple": temple,
                "zone": zone_name,
                "zone_density": zone_density,
                "risk_level": "CRITICAL",
                "recommended_immediate_action": (
                    f"Immediate queue relief required at {zone_name}. "
                    "Halt upstream inflow, open emergency bypass gates, and dispatch marshals."
                ),
            })

    # 8. Assemble Unified Intelligence Payload
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "temple": temple,
        "timestamp": timestamp_str,
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
            "zones": temple_zones,
        },
        "zones": temple_zones,
        "crowd_intelligence": {
            "final_crowd_score": final_crowd_score,
            "final_risk_level": final_risk_level,
            "trend": trend,
            "recommended_action": recommended_action,
        },
        "alerts": alerts,
    }


if __name__ == "__main__":
    print("=" * 75)
    print(">> YATRASAFE CROWD INTELLIGENCE ENGINE TEST SUITE")
    print("=" * 75)

    # Test Scenario 1: Somnath Normal Weekday
    print("\n--- TEST SCENARIO 1: Somnath Normal Weekday (Wednesday 10:00 AM) ---")
    scenario_1 = analyze_temple(
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
    print(json.dumps(scenario_1, indent=4))

    # Test Scenario 2: Dwarka Busy Weekend
    print("\n--- TEST SCENARIO 2: Dwarka Busy Weekend (Saturday 08:00 AM) ---")
    scenario_2 = analyze_temple(
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
    print(json.dumps(scenario_2, indent=4))

    # Test Scenario 3: Ambaji Major Festival Day
    print("\n--- TEST SCENARIO 3: Ambaji Major Festival Day (Navratri / Festival Evening) ---")
    scenario_3 = analyze_temple(
        temple="Ambaji",
        hour=18,
        day_of_week="Sunday",
        is_weekend=1,
        is_holiday=1,
        is_festival=1,
        weather="Sunny",
        temperature=30.0,
        previous_visitors=5000,
    )
    print(json.dumps(scenario_3, indent=4))

    print("\n" + "=" * 75)
    print(">> All Crowd Intelligence test scenarios executed successfully.")
    print("=" * 75)
