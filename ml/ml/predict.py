"""
AI Crowd Prediction Engine for YatraSafe AI Module.

Loads the trained machine learning pipeline from models/crowd_model.pkl
and provides real-time crowd density forecasting, capacity saturation analysis,
crowd safety risk categorization, and operational action recommendations.
"""

import json
import os
import sys
import joblib
import pandas as pd

# Temple capacity definitions (maximum nominal complex capacity for 4 Gujarat pilgrimage sites)
TEMPLE_CAPACITIES = {
    "Somnath": 40000,
    "Dwarka": 35000,
    "Ambaji": 50000,
    "Pavagadh": 25000,
}

SUPPORTED_TEMPLES = list(TEMPLE_CAPACITIES.keys())
SUPPORTED_WEATHER = ["Sunny", "Cloudy", "Rainy", "Clear", "Heavy Rain"]

# Action recommendation templates based on safety risk levels
RISK_ACTIONS = {
    "LOW": "Normal operations. No immediate action required.",
    "MODERATE": "Monitor crowd closely and prepare additional staff if crowd increases.",
    "HIGH": "Deploy additional security staff, monitor entry gates, and prepare alternate queue routing.",
    "CRITICAL": "Open additional gates, restrict new entry if necessary, redirect pilgrims to alternate routes, and alert emergency response teams.",
}

# Global cached model pipeline instance
_MODEL_PIPELINE = None


def get_model_pipeline(model_path: str = None):
    """Load and cache the trained ML pipeline."""
    global _MODEL_PIPELINE
    if _MODEL_PIPELINE is None:
        if model_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            model_path = os.path.join(project_root, "models", "crowd_model.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Trained model artifact not found at: {model_path}. Please run ml/train.py first."
            )
        _MODEL_PIPELINE = joblib.load(model_path)
    return _MODEL_PIPELINE


def get_risk_level(crowd_percentage: float) -> str:
    """Classify crowd percentage into standard safety risk tiers."""
    if crowd_percentage < 40.0:
        return "LOW"
    elif crowd_percentage < 70.0:
        return "MODERATE"
    elif crowd_percentage < 85.0:
        return "HIGH"
    else:
        return "CRITICAL"


def predict_crowd(
    temple: str,
    hour: int,
    day_of_week: str,
    is_weekend: int,
    is_holiday: int,
    is_festival: int,
    weather: str,
    temperature: float,
    previous_visitors: int,
    current_crowd: int,
    model_path: str = None
) -> dict:
    """
    Predict crowd volume, capacity utilization, and risk recommendations.

    Parameters:
        temple (str): Target temple name.
        hour (int): Hour of day (0 to 23).
        day_of_week (str): Day of week (e.g. 'Monday', 'Saturday').
        is_weekend (int): 1 if Saturday or Sunday, else 0.
        is_holiday (int): 1 if public holiday, else 0.
        is_festival (int): 1 if religious festival, else 0.
        weather (str): Weather condition ('Sunny', 'Cloudy', 'Rainy', 'Clear', 'Heavy Rain').
        temperature (float): Temperature in Celsius.
        previous_visitors (int): Visitor inflow count in previous hour (>= 0).
        current_crowd (int): Active crowd accumulation in complex (>= 0).
        model_path (str, optional): Custom model file path.

    Returns:
        dict: Standardized prediction response dictionary.
    """
    # 1. Input Validation
    if temple not in SUPPORTED_TEMPLES:
        raise ValueError(
            f"Unsupported temple '{temple}'. Supported temples are: {SUPPORTED_TEMPLES}"
        )

    if not isinstance(hour, int) or not (0 <= hour <= 23):
        raise ValueError(f"Hour must be an integer between 0 and 23. Received: {hour}")

    if weather not in SUPPORTED_WEATHER:
        raise ValueError(
            f"Unsupported weather condition '{weather}'. Supported weather values are: {SUPPORTED_WEATHER}"
        )

    if previous_visitors < 0:
        raise ValueError(
            f"previous_visitors must be non-negative. Received: {previous_visitors}"
        )

    if current_crowd < 0:
        raise ValueError(
            f"current_crowd must be non-negative. Received: {current_crowd}"
        )

    if is_weekend not in (0, 1):
        raise ValueError(f"is_weekend must be 0 or 1. Received: {is_weekend}")

    if is_holiday not in (0, 1):
        raise ValueError(f"is_holiday must be 0 or 1. Received: {is_holiday}")

    if is_festival not in (0, 1):
        raise ValueError(f"is_festival must be 0 or 1. Received: {is_festival}")

    # 2. Build input DataFrame matching model features
    input_df = pd.DataFrame([
        {
            "temple": temple,
            "day_of_week": day_of_week,
            "weather": weather,
            "hour": hour,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "is_festival": is_festival,
            "temperature": float(temperature),
            "previous_visitors": int(previous_visitors),
            "current_crowd": int(current_crowd),
        }
    ])

    # 3. Model Inference
    pipeline = get_model_pipeline(model_path)
    raw_prediction = pipeline.predict(input_df)[0]
    predicted_visitors = int(max(0, round(float(raw_prediction))))

    # 4. Capacity & Risk Calculation
    temple_capacity = TEMPLE_CAPACITIES[temple]
    raw_crowd_percentage = (predicted_visitors / temple_capacity) * 100.0
    crowd_percentage = round(min(100.0, max(0.0, raw_crowd_percentage)), 2)

    risk_level = get_risk_level(crowd_percentage)
    recommended_action = RISK_ACTIONS[risk_level]

    # 5. Formatted Return Dictionary
    return {
        "temple": temple,
        "predicted_visitors": predicted_visitors,
        "temple_capacity": temple_capacity,
        "crowd_percentage": crowd_percentage,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
    }


if __name__ == "__main__":
    print("=" * 70)
    print(">> YATRASAFE AI CROWD INFERENCE ENGINE TEST SUITE")
    print("=" * 70)

    # Test Case 1: Normal Weekday Scenario (Somnath)
    print("\n--- TEST CASE 1: Normal Weekday Scenario (Somnath, Tuesday 2:00 PM) ---")
    test_1 = predict_crowd(
        temple="Somnath",
        hour=14,
        day_of_week="Tuesday",
        is_weekend=0,
        is_holiday=0,
        is_festival=0,
        weather="Sunny",
        temperature=31.5,
        previous_visitors=950,
        current_crowd=2400,
    )
    print(json.dumps(test_1, indent=4))

    # Test Case 2: Busy Weekend Scenario (Dwarka)
    print("\n--- TEST CASE 2: Busy Weekend Morning Darshan (Dwarka, Saturday 8:00 AM) ---")
    test_2 = predict_crowd(
        temple="Dwarka",
        hour=8,
        day_of_week="Saturday",
        is_weekend=1,
        is_holiday=0,
        is_festival=0,
        weather="Clear",
        temperature=30.0,
        previous_visitors=2200,
        current_crowd=5500,
    )
    print(json.dumps(test_2, indent=4))

    # Test Case 3: Major Festival Scenario (Ambaji)
    print("\n--- TEST CASE 3: Major Festival Surge (Ambaji, Bhadarvi Poonam / Navratri) ---")
    test_3 = predict_crowd(
        temple="Ambaji",
        hour=18,
        day_of_week="Sunday",
        is_weekend=1,
        is_holiday=1,
        is_festival=1,
        weather="Clear",
        temperature=29.0,
        previous_visitors=4500,
        current_crowd=12000,
    )
    print(json.dumps(test_3, indent=4))

    # Test Case 4: Hilltop Pilgrimage Shrine (Pavagadh, Hilltop Peak)
    print("\n--- TEST CASE 4: Hilltop Shrine Weather Impact (Pavagadh, Sunday Afternoon) ---")
    test_4 = predict_crowd(
        temple="Pavagadh",
        hour=16,
        day_of_week="Sunday",
        is_weekend=1,
        is_holiday=0,
        is_festival=0,
        weather="Clear",
        temperature=32.0,
        previous_visitors=1800,
        current_crowd=4500,
    )
    print(json.dumps(test_4, indent=4))

    print("\n" + "=" * 70)
    print(">> All 4 Gujarat test scenarios executed successfully.")
    print("=" * 70)
