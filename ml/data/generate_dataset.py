"""
Synthetic Historical Dataset Generator for YatraSafe AI Module.

Generates realistic hourly historical crowd metrics for the 4 Gujarat pilgrimage sites:
- Somnath (Prabhas Patan, Gir Somnath, Gujarat)
- Dwarka (Dwarkadhish Temple, Devbhumi Dwarka, Gujarat)
- Ambaji (Arasur Hill, Banaskantha, Gujarat)
- Pavagadh (Kalika Mata Temple, Panchmahal, Gujarat)

Simulates time-of-day darshan peaks, weekend surges, festival spikes,
weather impact, dwell dynamics, and temple-specific capacities.
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Set fixed random seed for 100% reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

TEMPLES = {
    "Somnath": {
        "base_visitors": 1200,
        "dwell_retention": 0.45,
        "temp_range": (20.0, 35.0),
        "special_day": "Monday",
        "special_day_boost": 1.35,  # Somnath Lord Shiva special
        "rain_sensitivity": 0.75,
    },
    "Dwarka": {
        "base_visitors": 1100,
        "dwell_retention": 0.48,
        "temp_range": (21.0, 36.0),
        "special_day": "Sunday",
        "special_day_boost": 1.30,  # Dwarkadhish weekend pilgrim peak
        "rain_sensitivity": 0.78,
    },
    "Ambaji": {
        "base_visitors": 1400,
        "dwell_retention": 0.52,
        "temp_range": (19.0, 38.0),
        "special_day": "Sunday",
        "special_day_boost": 1.40,  # Amba Mata Sunday/Poonam peak
        "rain_sensitivity": 0.70,
    },
    "Pavagadh": {
        "base_visitors": 950,
        "dwell_retention": 0.55,
        "temp_range": (20.0, 39.0),
        "special_day": "Sunday",
        "special_day_boost": 1.45,  # Kalika Mata hilltop surge
        "rain_sensitivity": 0.65,
    },
}

# Hourly darshan multiplier (0:00 to 23:00)
HOURLY_MULTIPLIERS = [
    0.03, 0.02, 0.02, 0.05, 0.35, 0.75,  # 00:00 - 05:00: Night / Early Mangala Aarti
    1.35, 1.70, 1.85, 1.65, 1.40, 1.15,  # 06:00 - 11:00: Peak Morning Darshan
    0.80, 0.70, 0.85, 1.10, 1.45, 1.80,  # 12:00 - 17:00: Afternoon dip -> Evening buildup
    1.95, 1.60, 1.20, 0.70, 0.30, 0.10   # 18:00 - 23:00: Peak Evening Sandhya Aarti -> Night closing
]

DAY_NAME_MULTIPLIERS = {
    "Monday": 1.00,
    "Tuesday": 0.92,
    "Wednesday": 0.94,
    "Thursday": 0.98,
    "Friday": 1.15,
    "Saturday": 1.60,
    "Sunday": 1.65,
}

# Specific festival dates in 2025
FESTIVAL_DATES = {
    "2025-01-14": "Makar Sankranti",
    "2025-01-15": "Uttarayan Festival",
    "2025-01-26": "Republic Day",
    "2025-02-26": "Maha Shivratri (Somnath Mega Surge)",
    "2025-03-14": "Holi",
    "2025-03-30": "Chaitra Navratri / Gudi Padwa",
    "2025-04-06": "Rama Navami",
    "2025-04-14": "Dr. Ambedkar Jayanti",
    "2025-04-20": "Akshaya Tritiya",
}

# Public / Gazetted holidays
HOLIDAY_DATES = {
    "2025-01-01": "New Year Day",
    "2025-01-14": "Makar Sankranti",
    "2025-01-26": "Republic Day",
    "2025-02-26": "Maha Shivratri",
    "2025-03-14": "Holi",
    "2025-03-30": "Cheti Chand / Navratri Start",
    "2025-03-31": "Eid-ul-Fitr",
    "2025-04-06": "Rama Navami",
    "2025-04-14": "Dr. Ambedkar Jayanti",
    "2025-04-18": "Good Friday",
}


def generate_crowd_dataset(
    start_date_str: str = "2025-01-01",
    num_days: int = 150,
    output_path: str = "data/historical_crowd.csv"
) -> pd.DataFrame:
    """Generate realistic hourly crowd data across the 4 Gujarat pilgrimage shrines."""
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    all_rows = []

    weather_types = ["Clear", "Sunny", "Cloudy", "Rainy", "Heavy Rain"]

    for temple, config in TEMPLES.items():
        base_val = config["base_visitors"]
        retention = config["dwell_retention"]
        temp_min, temp_max = config["temp_range"]
        rain_sens = config["rain_sensitivity"]
        special_day = config["special_day"]
        special_boost = config["special_day_boost"]

        # Track continuous state for lag features
        current_active_crowd = int(base_val * 0.2)
        prev_hour_visitors = int(base_val * 0.05)

        for day_offset in range(num_days):
            current_day = start_date + timedelta(days=day_offset)
            date_str = current_day.strftime("%Y-%m-%d")
            day_of_week = current_day.strftime("%A")
            is_weekend = 1 if day_of_week in ["Saturday", "Sunday"] else 0
            is_holiday = 1 if date_str in HOLIDAY_DATES else 0
            is_festival = 1 if date_str in FESTIVAL_DATES else 0

            # Daily weather condition profile for Gujarat pilgrimage locations
            weather_weights = [0.55, 0.25, 0.12, 0.06, 0.02]
            day_weather = np.random.choice(weather_types, p=weather_weights)

            # Daily baseline temperature with hourly diurnal cycle
            day_base_temp = np.random.uniform(temp_min + 3, temp_max - 3)

            for hour in range(24):
                # Hourly diurnal temperature curve (coolest at 5 AM, hottest at 2 PM)
                temp_variation = np.sin((hour - 8) / 24.0 * 2 * np.pi) * ((temp_max - temp_min) * 0.35)
                noise_temp = np.random.normal(0, 0.6)
                temperature = round(float(np.clip(day_base_temp + temp_variation + noise_temp, temp_min - 2, temp_max + 2)), 1)

                # Hourly weather adjustments
                hour_weather = day_weather
                # Occasional afternoon rain transition
                if day_weather in ["Cloudy", "Rainy"] and hour in [14, 15, 16, 17]:
                    if np.random.rand() < 0.35:
                        hour_weather = "Heavy Rain" if day_weather == "Rainy" else "Rainy"
                elif day_weather == "Heavy Rain" and hour in [0, 1, 2, 3, 22, 23]:
                    hour_weather = "Rainy"

                # Multipliers calculation
                h_mult = HOURLY_MULTIPLIERS[hour]
                d_mult = DAY_NAME_MULTIPLIERS[day_of_week]

                # Special deity day boost
                if day_of_week == special_day:
                    d_mult *= special_boost

                # Festival & Holiday multipliers
                fest_mult = 1.0
                if is_festival:
                    fest_mult = np.random.uniform(1.85, 2.50)
                elif is_holiday:
                    fest_mult = np.random.uniform(1.30, 1.55)

                # Weather penalty multiplier
                weather_mult = 1.0
                if hour_weather == "Cloudy":
                    weather_mult = 0.96
                elif hour_weather == "Rainy":
                    weather_mult = rain_sens
                elif hour_weather == "Heavy Rain":
                    weather_mult = rain_sens * 0.55

                # Controlled random noise
                random_noise = np.random.lognormal(mean=0.0, sigma=0.12)

                # Final hourly incoming visitors calculation
                expected_visitors = base_val * h_mult * d_mult * fest_mult * weather_mult * random_noise
                visitors = int(max(5, round(expected_visitors)))

                # Current active crowd in complex calculation (Queue Dwell dynamics)
                dwell_noise = np.random.normal(1.0, 0.05)
                effective_retention = min(0.85, retention * dwell_noise)
                current_active_crowd = int(max(visitors, round(current_active_crowd * effective_retention + visitors * 1.35)))

                # Append record
                all_rows.append({
                    "temple": temple,
                    "date": date_str,
                    "hour": hour,
                    "day_of_week": day_of_week,
                    "is_weekend": is_weekend,
                    "is_holiday": is_holiday,
                    "is_festival": is_festival,
                    "weather": hour_weather,
                    "temperature": temperature,
                    "previous_visitors": prev_hour_visitors,
                    "current_crowd": current_active_crowd,
                    "visitors": visitors,
                })

                # Update lag for next hour
                prev_hour_visitors = visitors

    df = pd.DataFrame(all_rows)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    csv_file_path = os.path.join(current_dir, "historical_crowd.csv")

    print(f"Generating realistic crowd dataset for 4 Gujarat temples at: {csv_file_path} ...")
    # 4 temples * 150 days * 24 hours = 14,400 rows (>= 10,000 required)
    df = generate_crowd_dataset(
        start_date_str="2025-01-01",
        num_days=150,
        output_path=csv_file_path
    )

    print("\n" + "=" * 60)
    print(">> DATASET GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total Rows: {len(df):,}")
    print(f"Temples: {df['temple'].unique().tolist()}")
    print(f"Missing Values: {df.isnull().sum().sum()}")
    print("\nTemple-wise Distribution:")
    print(df["temple"].value_counts().to_string())
