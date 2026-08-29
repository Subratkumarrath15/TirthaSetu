import json
import urllib.error
import urllib.request

base = "http://127.0.0.1:8000"


def test_url(name, path):
    url = f"{base}{path}"
    print("\n" + "=" * 60)
    print(f"TEST: {name}")
    print(f"URL:  {url}")
    print("=" * 60)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            print(f"Status: {status} OK")
            print(json.dumps(body, indent=2))
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    # Test 1: Health
    test_url("1. Health Check", "/health")

    # Test 2: Temples
    test_url("2. List Supported Gujarat Temples", "/api/temples")

    # Test 3: Real-time Telemetry
    test_url("3. Real-time Sensor Telemetry (Somnath)", "/api/realtime/Somnath")

    # Test 4: AI Prediction
    test_url(
        "4. AI Prediction (Ambaji Festival Sunday)",
        "/api/predict/Ambaji?hour=18&day_of_week=Sunday&is_weekend=1&is_holiday=1&is_festival=1&weather=Sunny&temperature=31.0&previous_visitors=4500&current_crowd=12000",
    )

    # Test 5: Crowd Intelligence
    test_url(
        "5. Unified Crowd Intelligence (Somnath Normal Weekday)",
        "/api/intelligence/Somnath?hour=10&day_of_week=Wednesday&is_weekend=0&is_holiday=0&is_festival=0&weather=Clear&temperature=28.0&previous_visitors=750",
    )

    # Test 6: 404 Error Handling for old temple
    test_url("6. Error Handling (Old / Unsupported Temple Tirupati 404)", "/api/realtime/Tirupati")
