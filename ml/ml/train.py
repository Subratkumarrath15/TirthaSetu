"""
AI Crowd Prediction Model Training Pipeline for YatraSafe AI Module.

Trains an end-to-end Machine Learning pipeline (OneHotEncoding + RandomForestRegressor)
to predict hourly visitor inflow for pilgrimage temple sites based on temporal,
meteorological, calendar, and autoregressive crowd features.
"""

import json
import os
import sys
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def train_model():
    print("=" * 70)
    print(">> YATRASAFE AI CROWD PREDICTION MODEL TRAINING")
    print("=" * 70)

    # Base paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, "data", "historical_crowd.csv")
    models_dir = os.path.join(project_root, "models")
    model_output_path = os.path.join(models_dir, "crowd_model.pkl")
    metrics_output_path = os.path.join(models_dir, "model_metrics.json")

    # 1. Check file existence
    if not os.path.exists(data_path):
        print(f"[ERROR] Historical dataset not found at: {data_path}")
        sys.exit(1)

    print(f"\n1. Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"   Loaded {len(df):,} rows and {len(df.columns)} columns.")

    # 2. Define Features and Target
    categorical_cols = ["temple", "day_of_week", "weather"]
    numerical_cols = [
        "hour", "is_weekend", "is_holiday", "is_festival",
        "temperature", "previous_visitors", "current_crowd"
    ]
    target_col = "visitors"

    # Check required columns
    all_required = categorical_cols + numerical_cols + [target_col]
    missing_cols = [c for c in all_required if c not in df.columns]
    if missing_cols:
        print(f"[ERROR] Missing required columns in dataset: {missing_cols}")
        sys.exit(1)

    X = df[categorical_cols + numerical_cols]
    y = df[target_col]

    print(f"\n2. Features Configured:")
    print(f"   Categorical Features ({len(categorical_cols)}): {categorical_cols}")
    print(f"   Numerical Features   ({len(numerical_cols)}): {numerical_cols}")
    print(f"   Target Variable:                 '{target_col}'")

    # 3. Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"\n3. Data Split:")
    print(f"   Training Set: {len(X_train):,} samples (80%)")
    print(f"   Testing Set:  {len(X_test):,} samples (20%)")

    # 4. Construct Preprocessor with ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
            ("num", "passthrough", numerical_cols),
        ]
    )

    # 5. Build Complete Pipeline (Preprocessor + Regressor)
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=200,
                    random_state=42,
                    n_jobs=-1
                ),
            ),
        ]
    )

    # 6. Train the Pipeline
    print("\n4. Training RandomForestRegressor Pipeline (200 estimators, parallel)...")
    start_time = datetime.now()
    pipeline.fit(X_train, y_train)
    training_duration = (datetime.now() - start_time).total_seconds()
    print(f"   Model training completed in {training_duration:.2f} seconds.")

    # 7. Evaluate on Test Set
    print("\n5. Evaluating Model on Test Set...")
    y_pred = pipeline.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    print("-" * 50)
    print(f"   Mean Absolute Error (MAE):      {mae:10.2f} visitors")
    print(f"   Root Mean Squared Error (RMSE): {rmse:10.2f} visitors")
    print(f"   R-squared Score (R2):           {r2:10.4f} ({r2 * 100:.2f}%)")
    print("-" * 50)

    # 8. Save Trained Model Pipeline (with compression to save disk space)
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(pipeline, model_output_path, compress=3)
    print(f"\n6. Trained Pipeline saved to: {model_output_path}")

    # 9. Save Model Metrics JSON
    training_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metrics_data = {
        "model_name": "RandomForestRegressor",
        "training_datetime": training_timestamp,
        "n_estimators": 200,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "features": {
            "categorical": categorical_cols,
            "numerical": numerical_cols,
        },
        "metrics": {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2_score": round(r2, 4),
        },
    }

    with open(metrics_output_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)
    print(f"   Evaluation metrics saved to:  {metrics_output_path}")

    # 10. Test Saved Model with Sample Input
    print("\n7. Testing Saved Model with Sample Prediction:")
    loaded_pipeline = joblib.load(model_output_path)

    sample_index = X_test.index[0]
    sample_input = X_test.loc[[sample_index]]
    actual_visitors = int(y_test.loc[sample_index])
    predicted_visitors = float(loaded_pipeline.predict(sample_input)[0])
    diff = predicted_visitors - actual_visitors
    pct_diff = (abs(diff) / actual_visitors) * 100 if actual_visitors > 0 else 0

    print("   Sample Input:")
    for col, val in sample_input.iloc[0].to_dict().items():
        print(f"     {col:<18} : {val}")
    print(f"   ----------------------------------------")
    print(f"   Actual Visitors:       {actual_visitors:,}")
    print(f"   Predicted Visitors:    {round(predicted_visitors):,}")
    print(f"   Prediction Difference: {diff:+.2f} ({pct_diff:.2f}%)")

    # 11. Final Success Confirmation
    print("\n" + "=" * 70)
    print(">> AI crowd prediction model trained and saved successfully")
    print("=" * 70)


if __name__ == "__main__":
    train_model()
