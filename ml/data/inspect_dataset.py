"""
Dataset Inspection and Validation Script for YatraSafe AI Module.

Validates the integrity, schema, data quality, distribution patterns,
and readiness of data/historical_crowd.csv prior to ML model training.
"""

import os
import sys
import pandas as pd
import numpy as np


def inspect_and_validate(csv_path: str):
    print("=" * 70)
    print(">> YATRASAFE DATASET INSPECTION & VALIDATION PIPELINE")
    print("=" * 70)

    if not os.path.exists(csv_path):
        print(f"[ERROR] Dataset file not found at: {csv_path}")
        sys.exit(1)

    print(f"\nLoading dataset from: {csv_path} ...")
    df = pd.read_csv(csv_path)
    issues_found = []

    # 1. Dataset Shape
    print("\n--- 1. DATASET SHAPE ---")
    rows, cols = df.shape
    print(f"Total Rows:    {rows:,}")
    print(f"Total Columns: {cols}")

    if rows < 10000:
        issues_found.append(f"Row count {rows} is below recommended minimum of 10,000.")

    # 2. Column Names
    print("\n--- 2. COLUMN NAMES ---")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")

    expected_cols = [
        "temple", "date", "hour", "day_of_week", "is_weekend",
        "is_holiday", "is_festival", "weather", "temperature",
        "previous_visitors", "current_crowd", "visitors"
    ]
    missing_expected = [c for c in expected_cols if c not in df.columns]
    if missing_expected:
        issues_found.append(f"Missing expected columns: {missing_expected}")

    # 3. First 10 Rows
    print("\n--- 3. FIRST 10 ROWS ---")
    print(df.head(10).to_string(index=True))

    # 4. Data Types for Every Column
    print("\n--- 4. COLUMN DATA TYPES ---")
    for col, dtype in df.dtypes.items():
        print(f"  {col:<20} : {dtype}")

    # 5. Missing Values in Every Column
    print("\n--- 5. MISSING VALUE ANALYSIS ---")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        pct = (count / rows) * 100
        print(f"  {col:<20} : {count:5d} missing ({pct:.2f}%)")

    total_nulls = null_counts.sum()
    print(f"  Total Missing Values : {total_nulls}")
    if total_nulls > 0:
        issues_found.append(f"Dataset contains {total_nulls} missing values.")

    # 6. Duplicate Row Count
    print("\n--- 6. DUPLICATE ROW ANALYSIS ---")
    duplicate_count = df.duplicated().sum()
    print(f"  Duplicate Rows Found: {duplicate_count}")
    if duplicate_count > 0:
        issues_found.append(f"Dataset contains {duplicate_count} duplicate rows.")

    # 7. Descriptive Statistics for Numerical Columns
    print("\n--- 7. DESCRIPTIVE STATISTICS (NUMERICAL COLUMNS) ---")
    num_df = df.select_dtypes(include=[np.number])
    print(num_df.describe().round(2).to_string())

    # 8. Number of Records for Each Temple
    print("\n--- 8. RECORD COUNT PER TEMPLE ---")
    temple_counts = df["temple"].value_counts()
    for temple, count in temple_counts.items():
        print(f"  {temple:<15} : {count:5d} records ({count/rows*100:.1f}%)")

    # 9. Average Visitors for Each Temple
    print("\n--- 9. AVERAGE VISITORS PER TEMPLE ---")
    temple_visitors = df.groupby("temple")["visitors"].agg(["mean", "median", "std", "min", "max"]).round(1)
    temple_visitors.columns = ["Mean Visitors", "Median Visitors", "Std Dev", "Min Visitors", "Max Visitors"]
    print(temple_visitors.to_string())

    # 10. Average Visitors by Hour
    print("\n--- 10. AVERAGE VISITORS BY HOUR (0 - 23) ---")
    hourly_avg = df.groupby("hour")["visitors"].mean().round(1)
    for hour, avg in hourly_avg.items():
        bar = "#" * int(avg / 120)
        print(f"  Hour {hour:02d}:00 | Avg: {avg:7.1f} visitors | {bar}")

    # 11. Average Visitors for Normal Days, Weekends, Holidays, Festivals
    print("\n--- 11. AVERAGE VISITORS BY CALENDAR / EVENT TYPE ---")
    normal_mask = (df["is_weekend"] == 0) & (df["is_holiday"] == 0) & (df["is_festival"] == 0)
    normal_avg = df.loc[normal_mask, "visitors"].mean()
    weekend_avg = df.loc[df["is_weekend"] == 1, "visitors"].mean()
    holiday_avg = df.loc[df["is_holiday"] == 1, "visitors"].mean()
    festival_avg = df.loc[df["is_festival"] == 1, "visitors"].mean()

    print(f"  Normal Weekdays (Non-holiday/festival) : {normal_avg:7.1f} visitors/hr (Baseline: 1.00x)")
    print(f"  Weekends (Saturday & Sunday)           : {weekend_avg:7.1f} visitors/hr (x{weekend_avg/normal_avg:.2f} vs Normal)")
    print(f"  Holidays                               : {holiday_avg:7.1f} visitors/hr (x{holiday_avg/normal_avg:.2f} vs Normal)")
    print(f"  Festival Days                          : {festival_avg:7.1f} visitors/hr (x{festival_avg/normal_avg:.2f} vs Normal)")

    # 12. Visitor Averages Grouped by Weather
    print("\n--- 12. AVERAGE VISITORS BY WEATHER CONDITION ---")
    weather_stats = df.groupby("weather")["visitors"].agg(["count", "mean", "std"]).round(1)
    weather_stats.columns = ["Records", "Mean Visitors", "Std Dev"]
    print(weather_stats.sort_values(by="Mean Visitors", ascending=False).to_string())

    # 13. Check Target Column 'visitors'
    print("\n--- 13. TARGET COLUMN 'visitors' INTEGRITY CHECK ---")
    if "visitors" not in df.columns:
        issues_found.append("Target column 'visitors' is missing from the dataset.")
        print("  [FAIL] Target column 'visitors' does NOT exist.")
    else:
        print("  [PASS] Target column 'visitors' exists.")
        neg_count = (df["visitors"] < 0).sum()
        nan_count = df["visitors"].isna().sum()
        min_val = df["visitors"].min()
        max_val = df["visitors"].max()
        print(f"  [PASS] Negative values count: {neg_count}")
        print(f"  [PASS] NaN / Null count:     {nan_count}")
        print(f"  [PASS] Value range:          {min_val} to {max_val:,} visitors")

        if neg_count > 0:
            issues_found.append(f"Target column contains {neg_count} negative values.")
        if nan_count > 0:
            issues_found.append(f"Target column contains {nan_count} NaN values.")
        if min_val < 0:
            issues_found.append(f"Target column has minimum value {min_val} < 0.")

    # 14. Final Validation Message
    print("\n" + "=" * 70)
    print("--- 14. FINAL VALIDATION STATUS ---")
    if not issues_found:
        print(">> Dataset validation successful - ready for ML training")
    else:
        print(">> [VALIDATION ISSUES DETECTED]")
        for issue in issues_found:
            print(f"   - {issue}")
    print("=" * 70)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "historical_crowd.csv")
    inspect_and_validate(csv_path)
