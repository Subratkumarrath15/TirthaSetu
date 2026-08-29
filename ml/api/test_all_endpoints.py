"""
Comprehensive Test Suite for all YatraSafe FastAPI Endpoints (4 Gujarat Shrines).
"""

import json
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def execute_test(name: str, endpoint: str, params: dict = None):
    query_str = f"?{urllib.parse.urlencode(params)}" if params else ""
    full_url = f"{BASE_URL}{endpoint}{query_str}"

    print("\n" + "=" * 70)
    print(f">> TEST: {name}")
    print(f">> URL:  {full_url}")
    print("=" * 70)

    try:
        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            print(f"HTTP Status: {status} OK")
            print(json.dumps(body, indent=2))
            return body
    except urllib.error.HTTPError as err:
        print(f"HTTP Error {err.code}: {err.read().decode('utf-8')}")
        return None
    except Exception as err:
        print(f"Network Error: {err}")
        return None


if __name__ == "__main__":
    # Test Parameters
    test_params = {
        "hour": 10,
        "day_of_week": "Thursday",
        "is_weekend": 0,
        "is_holiday": 0,
        "is_festival": 0,
        "weather": "Sunny",
        "temperature": 30,
        "previous_visitors": 4500,
    }

    # 1. Health Check
    execute_test("1. Service Health Check", "/health")

    # 2. Supported Temples
    execute_test("2. List Supported Temples", "/api/temples")

    # 3. Real-Time Telemetry (Somnath)
    execute_test("3. Real-Time Sensor Telemetry (Somnath)", "/api/realtime/Somnath")

    # 4. AI Prediction (Ambaji)
    predict_params = dict(test_params)
    predict_params["current_crowd"] = 8000
    execute_test("4. AI Prediction (Ambaji)", "/api/predict/Ambaji", predict_params)

    # 5. Crowd Intelligence (Somnath)
    execute_test("5. Crowd Intelligence (Somnath)", "/api/intelligence/Somnath", test_params)

    # 6. Resource Recommendations (Dwarka)
    execute_test("6. Resource Recommendations (Dwarka)", "/api/recommendations/Dwarka", test_params)

    # 7. Full Status (Pavagadh)
    execute_test("7. Full Status & Resource Directives (Pavagadh)", "/api/full-status/Pavagadh", test_params)
