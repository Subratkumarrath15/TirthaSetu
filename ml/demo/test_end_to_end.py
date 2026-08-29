"""
Master End-to-End Integration Test Suite for YatraSafe AI + Real-Time Intelligence System (4 Gujarat Shrines).

Tests the full end-to-end operational pipeline:
Historical Dataset -> ML Model -> Stateful IoT Simulator -> Crowd Intelligence ->
Risk & Trend Detection -> Alerts -> Resource Recommendations -> Incident Command ->
Analytics & Insights -> Government Dashboard APIs.
"""

import importlib
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Tuple

# Fix Windows console encoding if needed
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

BASE_URL = "http://127.0.0.1:8000"


def http_req(method: str, path: str, data: dict = None) -> Tuple[int, Dict[str, Any]]:
    """Helper to execute HTTP requests against the FastAPI server."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"} if data else {}
    body = json.dumps(data).encode("utf-8") if data else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        try:
            return err.code, json.loads(err.read().decode("utf-8"))
        except Exception:
            return err.code, {"error": err.reason}
    except Exception as exc:
        return 500, {"error": str(exc)}


class EndToEndTester:
    def __init__(self):
        self.results = {
            "components": {},
            "scenarios": {},
            "integration": {},
            "issues": [],
        }

    def log_issue(self, msg: str):
        print(f"  [!] ISSUE: {msg}")
        self.results["issues"].append(msg)

    # ------------------------------------------------------------------------
    # 1. SYSTEM HEALTH TESTS
    # ------------------------------------------------------------------------
    def test_system_health(self):
        print("\n" + "=" * 80)
        print(">> [1/6] SYSTEM HEALTH & COMPONENT INTEGRITY TESTS")
        print("=" * 80)

        # A. Dependencies
        deps = ["pandas", "numpy", "sklearn", "fastapi", "uvicorn", "joblib"]
        for d in deps:
            try:
                importlib.import_module(d)
                print(f"  [OK] Dependency: {d}")
            except ImportError:
                self.log_issue(f"Missing dependency: {d}")

        # B. Historical Dataset
        dataset_path = os.path.join(PROJECT_ROOT, "data", "historical_crowd.csv")
        if os.path.exists(dataset_path) and os.path.getsize(dataset_path) > 1000:
            print(f"  [OK] Dataset exists: {dataset_path} ({os.path.getsize(dataset_path):,} bytes)")
        else:
            self.log_issue(f"Historical dataset missing or empty at {dataset_path}")

        # C. ML Model
        model_path = os.path.join(PROJECT_ROOT, "models", "crowd_model.pkl")
        try:
            from ml.predict import get_model_pipeline, predict_crowd
            pipeline = get_model_pipeline()
            if pipeline is not None and os.path.exists(model_path):
                self.results["components"]["ML Model"] = True
                print(f"  [OK] ML Model loaded successfully: {model_path}")
            else:
                self.results["components"]["ML Model"] = False
                self.log_issue("ML model artifact not loaded in ml.predict")
        except Exception as e:
            self.results["components"]["ML Model"] = False
            self.log_issue(f"Failed to import/load ML model: {e}")

        # D. IoT Simulator
        try:
            from realtime.sensor_simulator import TempleSensorSimulator, ZONE_CONFIGS, calculate_risk_level
            sim = TempleSensorSimulator()
            step_record = sim.step()
            if step_record and len(ZONE_CONFIGS) == 4:
                self.results["components"]["IoT Simulator"] = True
                print("  [OK] Stateful IoT Simulator module imported & verified (4 Gujarat shrines)")
            else:
                self.results["components"]["IoT Simulator"] = False
                self.log_issue("IoT Simulator step execution failed")
        except Exception as e:
            self.results["components"]["IoT Simulator"] = False
            self.log_issue(f"Failed to import IoT Simulator: {e}")

        # E. Crowd Intelligence Engine
        try:
            from crowd_engine.crowd_engine import analyze_temple, calculate_final_risk_level
            self.results["components"]["Crowd Intelligence"] = True
            print("  [OK] Crowd Intelligence Engine imported")
        except Exception as e:
            self.results["components"]["Crowd Intelligence"] = False
            self.log_issue(f"Failed to import Crowd Intelligence: {e}")

        # F. Resource Engine
        try:
            from resource_engine.resource_recommender import recommend_resources
            self.results["components"]["Resource Engine"] = True
            print("  [OK] Resource Recommendation Engine imported")
        except Exception as e:
            self.results["components"]["Resource Engine"] = False
            self.log_issue(f"Failed to import Resource Engine: {e}")

        # G. Incident Command Center
        try:
            from api.incidents import incident_manager
            self.results["components"]["Incident Command Center"] = True
            print("  [OK] Incident Command Center module imported")
        except Exception as e:
            self.results["components"]["Incident Command Center"] = False
            self.log_issue(f"Failed to import Incident Command Center: {e}")

        # H. Analytics Engine
        try:
            from api.analytics import analytics_manager
            self.results["components"]["Analytics Engine"] = True
            print("  [OK] Analytics & Decision Insights module imported")
        except Exception as e:
            self.results["components"]["Analytics Engine"] = False
            self.log_issue(f"Failed to import Analytics: {e}")

        # I. FastAPI Application
        try:
            from api.prediction_api import app
            self.results["components"]["FastAPI"] = True
            print("  [OK] FastAPI Application imported")
        except Exception as e:
            self.results["components"]["FastAPI"] = False
            self.log_issue(f"Failed to import FastAPI application: {e}")

    # ------------------------------------------------------------------------
    # 2. ALL API ENDPOINT TESTS
    # ------------------------------------------------------------------------
    def test_api_endpoints(self):
        print("\n" + "=" * 80)
        print(">> [2/6] EXHAUSTIVE REST API ENDPOINT VALIDATION (4 GUJARAT SHRINES)")
        print("=" * 80)

        get_endpoints = [
            ("GET /health", "/health"),
            ("GET /api/temples", "/api/temples"),
            ("GET /api/realtime/Somnath", "/api/realtime/Somnath"),
            ("GET /api/realtime/Dwarka", "/api/realtime/Dwarka"),
            ("GET /api/realtime/Ambaji", "/api/realtime/Ambaji"),
            ("GET /api/realtime/Pavagadh", "/api/realtime/Pavagadh"),
            ("GET /api/predict/Somnath", "/api/predict/Somnath?hour=10&day_of_week=Wednesday&is_weekend=0&is_holiday=0&is_festival=0&weather=Sunny&temperature=30&previous_visitors=3000&current_crowd=8000"),
            ("GET /api/intelligence/Dwarka", "/api/intelligence/Dwarka?hour=10&day_of_week=Wednesday&is_weekend=0&is_holiday=0&is_festival=0&weather=Sunny&temperature=30&previous_visitors=3000"),
            ("GET /api/recommendations/Ambaji", "/api/recommendations/Ambaji?hour=10&day_of_week=Wednesday&is_weekend=0&is_holiday=0&is_festival=0&weather=Sunny&temperature=30&previous_visitors=3000"),
            ("GET /api/full-status/Pavagadh", "/api/full-status/Pavagadh?hour=10&day_of_week=Wednesday&is_weekend=0&is_holiday=0&is_festival=0&weather=Sunny&temperature=30&previous_visitors=3000"),
            ("GET /api/demo/scenarios", "/api/demo/scenarios"),
            ("GET /api/demo/normal-day", "/api/demo/normal-day"),
            ("GET /api/demo/busy-weekend", "/api/demo/busy-weekend"),
            ("GET /api/demo/festival-rush", "/api/demo/festival-rush"),
            ("GET /api/demo/emergency-overcrowding", "/api/demo/emergency-overcrowding"),
            ("GET /api/incidents/active", "/api/incidents/active"),
            ("GET /api/incidents/history", "/api/incidents/history"),
            ("GET /api/analytics/summary", "/api/analytics/summary"),
            ("GET /api/analytics/trends", "/api/analytics/trends"),
            ("GET /api/analytics/risk-distribution", "/api/analytics/risk-distribution"),
            ("GET /api/analytics/temple-comparison", "/api/analytics/temple-comparison"),
            ("GET /api/analytics/incidents", "/api/analytics/incidents"),
        ]

        for name, path in get_endpoints:
            status, res = http_req("GET", path)
            if status == 200:
                print(f"  [200 OK] {name}")
            else:
                self.log_issue(f"Endpoint {name} returned status {status}: {res}")

        # Test POST endpoints with an active incident from server
        print("\n  Testing POST Incident Lifecycle Endpoints:")
        # First trigger emergency demo to ensure fresh active incidents exist on the server
        http_req("GET", "/api/demo/emergency-overcrowding")
        st, inc_data = http_req("GET", "/api/incidents/active")
        active_list = inc_data.get("incidents", [])

        target_inc = next((i for i in active_list if i.get("status") == "ACTIVE"), active_list[0] if active_list else None)

        if target_inc:
            target_id = target_inc["incident_id"]

            # POST Acknowledge
            st_ack, res_ack = http_req("POST", f"/api/incidents/{target_id}/acknowledge")
            if st_ack == 200 and res_ack.get("incident", {}).get("status") == "ACKNOWLEDGED":
                print(f"  [200 OK] POST /api/incidents/{target_id}/acknowledge")
            else:
                self.log_issue(f"POST acknowledge failed for {target_id}: {res_ack}")

            # POST Resolve
            st_res, res_res = http_req("POST", f"/api/incidents/{target_id}/resolve")
            if st_res == 200 and res_res.get("incident", {}).get("status") == "RESOLVED":
                print(f"  [200 OK] POST /api/incidents/{target_id}/resolve")
            else:
                self.log_issue(f"POST resolve failed for {target_id}: {res_res}")
        else:
            self.log_issue("No active incident available to test acknowledge/resolve POST")

    # ------------------------------------------------------------------------
    # 3. FOUR DEMO SCENARIOS VALIDATION
    # ------------------------------------------------------------------------
    def test_demo_scenarios(self):
        print("\n" + "=" * 80)
        print(">> [3/6] DEMO SCENARIOS EXACT CALCULATED RESULTS VALIDATION")
        print("=" * 80)

        # 1. Normal Day (Somnath)
        st, res1 = http_req("GET", "/api/demo/normal-day")
        t1 = res1.get("temple")
        risk1 = res1.get("intelligence", {}).get("crowd_intelligence", {}).get("final_risk_level")
        score1 = res1.get("intelligence", {}).get("crowd_intelligence", {}).get("final_crowd_score")
        if st == 200 and risk1 == "LOW" and t1 == "Somnath":
            self.results["scenarios"]["Normal Day -> LOW (Somnath)"] = True
            print(f"  [OK] Scenario 1 (Normal Day): Somnath | Score {score1}% -> LOW (Pass)")
        else:
            self.results["scenarios"]["Normal Day -> LOW (Somnath)"] = False
            self.log_issue(f"Normal Day expected Somnath LOW, got {t1} {risk1} (Score: {score1})")

        # 2. Busy Weekend (Dwarka)
        st, res2 = http_req("GET", "/api/demo/busy-weekend")
        t2 = res2.get("temple")
        risk2 = res2.get("intelligence", {}).get("crowd_intelligence", {}).get("final_risk_level")
        score2 = res2.get("intelligence", {}).get("crowd_intelligence", {}).get("final_crowd_score")
        if st == 200 and risk2 == "MODERATE" and t2 == "Dwarka":
            self.results["scenarios"]["Busy Weekend -> MODERATE (Dwarka)"] = True
            print(f"  [OK] Scenario 2 (Busy Weekend): Dwarka | Score {score2}% -> MODERATE (Pass)")
        else:
            self.results["scenarios"]["Busy Weekend -> MODERATE (Dwarka)"] = False
            self.log_issue(f"Busy Weekend expected Dwarka MODERATE, got {t2} {risk2} (Score: {score2})")

        # 3. Festival Rush (Ambaji)
        st, res3 = http_req("GET", "/api/demo/festival-rush")
        t3 = res3.get("temple")
        risk3 = res3.get("intelligence", {}).get("crowd_intelligence", {}).get("final_risk_level")
        score3 = res3.get("intelligence", {}).get("crowd_intelligence", {}).get("final_crowd_score")
        if st == 200 and risk3 == "HIGH" and t3 == "Ambaji":
            self.results["scenarios"]["Festival Rush -> HIGH (Ambaji)"] = True
            print(f"  [OK] Scenario 3 (Festival Rush): Ambaji | Score {score3}% -> HIGH (Pass)")
        else:
            self.results["scenarios"]["Festival Rush -> HIGH (Ambaji)"] = False
            self.log_issue(f"Festival Rush expected Ambaji HIGH, got {t3} {risk3} (Score: {score3})")

        # 4. Emergency Overcrowding (Pavagadh)
        st, res4 = http_req("GET", "/api/demo/emergency-overcrowding")
        t4 = res4.get("temple")
        risk4 = res4.get("intelligence", {}).get("crowd_intelligence", {}).get("final_risk_level")
        score4 = res4.get("intelligence", {}).get("crowd_intelligence", {}).get("final_crowd_score")
        alerts4 = res4.get("intelligence", {}).get("alerts", [])
        resources4 = res4.get("resource_recommendations", {})
        prio4 = res4.get("emergency_priority")
        zones4 = res4.get("zones", [])

        # Check exact required parameters
        zone_map = {z["zone"]: z["crowd_density"] for z in zones4}
        d_mg = zone_map.get("Main Gate", 0.0)
        d_dq = zone_map.get("Darshan Queue", 0.0)
        d_te = zone_map.get("Temple Entrance", 0.0)
        d_pk = zone_map.get("Parking", 0.0)

        sec = resources4.get("security_personnel")
        med = resources4.get("medical_personnel")
        gates = resources4.get("additional_gates")

        passed_emergency = (
            st == 200
            and t4 == "Pavagadh"
            and risk4 == "CRITICAL"
            and len(alerts4) == 4
            and abs(d_mg - 92.0) < 0.1
            and abs(d_dq - 95.0) < 0.1
            and abs(d_te - 94.0) < 0.1
            and abs(d_pk - 90.0) < 0.1
            and sec == 20
            and med == 4
            and gates == 3
            and prio4 == "CRITICAL"
        )

        if passed_emergency:
            self.results["scenarios"]["Emergency -> CRITICAL (Pavagadh)"] = True
            print(f"  [OK] Scenario 4 (Emergency Overcrowding): Pavagadh | Score {score4}% -> CRITICAL")
            print("       - Exactly 4 Critical Alerts: True")
            print(f"       - Densities: Main Gate={d_mg}%, Queue={d_dq}%, Entrance={d_te}%, Parking={d_pk}%")
            print(f"       - Resources: Security={sec} units, Medical={med} units, Gates=+{gates}")
            print(f"       - Priority: {prio4}")
        else:
            self.results["scenarios"]["Emergency -> CRITICAL (Pavagadh)"] = False
            self.log_issue(
                f"Emergency Overcrowding failed validation: Temple={t4}, Risk={risk4}, Alerts={len(alerts4)}, "
                f"Densities=({d_mg}%, {d_dq}%, {d_te}%, {d_pk}%), Sec={sec}, Med={med}, Gates={gates}, Prio={prio4}"
            )

    # ------------------------------------------------------------------------
    # 4. CROSS-MODULE DATA CONSISTENCY
    # ------------------------------------------------------------------------
    def test_cross_module_consistency(self):
        print("\n" + "=" * 80)
        print(">> [4/6] CROSS-MODULE PIPELINE DATA CONSISTENCY")
        print("=" * 80)

        # A. AI -> Intelligence
        st, full_res = http_req(
            "GET",
            "/api/full-status/Somnath?hour=18&day_of_week=Sunday&is_weekend=1&is_holiday=1&is_festival=1&weather=Sunny&temperature=31&previous_visitors=6000"
        )
        ai_data = full_res.get("intelligence", {}).get("ai_prediction", {})
        crowd_data = full_res.get("intelligence", {}).get("crowd_intelligence", {})
        live_data = full_res.get("intelligence", {}).get("live_data", {})

        # Formula check: final_score == 0.40 * ai_percentage + 0.60 * live_density
        ai_pct = ai_data.get("crowd_percentage", 0.0)
        live_d = live_data.get("average_density", 0.0)
        score = crowd_data.get("final_crowd_score", 0.0)
        expected_score = round(min(100.0, max(0.0, (0.40 * ai_pct) + (0.60 * live_d))), 2)

        if abs(score - expected_score) <= 0.05:
            self.results["integration"]["AI -> Intelligence"] = True
            print(f"  [OK] AI -> Intelligence: Score {score}% matches 40/60 fusion formula ({expected_score}%)")
        else:
            self.results["integration"]["AI -> Intelligence"] = False
            self.log_issue(f"Fusion calculation mismatch: got {score}%, expected {expected_score}%")

        # B. Intelligence -> Resources
        res_ops = full_res.get("operations", {})
        res_recs = full_res.get("resource_recommendations", {})
        risk_lvl = crowd_data.get("final_risk_level")
        prio = full_res.get("emergency_priority")

        if risk_lvl == prio and "queue_action" in res_ops and "security_personnel" in res_recs:
            self.results["integration"]["Intelligence -> Resources"] = True
            print(f"  [OK] Intelligence -> Resources: Risk {risk_lvl} correctly dictates resource policy (Priority: {prio})")
        else:
            self.results["integration"]["Intelligence -> Resources"] = False
            self.log_issue("Intelligence to Resources policy mapping mismatch")

        # C. Alerts -> Incidents
        # Trigger emergency demo to ensure alerts create/update incidents
        http_req("GET", "/api/demo/emergency-overcrowding")
        st, inc_data = http_req("GET", "/api/incidents/active?temple=Pavagadh")
        pav_incidents = inc_data.get("incidents", [])

        if len(pav_incidents) >= 3:
            self.results["integration"]["Alerts -> Incidents"] = True
            print(f"  [OK] Alerts -> Incidents: Critical alerts successfully mapped to {len(pav_incidents)} active Pavagadh incidents")
        else:
            self.results["integration"]["Alerts -> Incidents"] = False
            self.log_issue(f"Alerts to Incidents sync failed, found {len(pav_incidents)} active Pavagadh incidents")

        # D. Intelligence -> Analytics
        st, sum_data = http_req("GET", "/api/analytics/summary")
        st, comp_data = http_req("GET", "/api/analytics/temple-comparison")
        st, dist_data = http_req("GET", "/api/analytics/risk-distribution")

        if (
            sum_data.get("total_snapshots_recorded", 0) > 0
            and len(comp_data.get("comparison", [])) == 4
            and sum(dist_data.get("percentages", {}).values()) > 99.0
        ):
            self.results["integration"]["Intelligence -> Analytics"] = True
            print(f"  [OK] Intelligence -> Analytics: Rolling snapshots active (Total: {sum_data.get('total_snapshots_recorded')}, Temples: 4)")
        else:
            self.results["integration"]["Intelligence -> Analytics"] = False
            self.log_issue("Analytics snapshot aggregation mismatch")

    # ------------------------------------------------------------------------
    # 5. ERROR HANDLING TESTS
    # ------------------------------------------------------------------------
    def test_error_handling(self):
        print("\n" + "=" * 80)
        print(">> [5/6] ERROR HANDLING & BOUNDARY VERIFICATION")
        print("=" * 80)

        # A. Invalid temple name (and old temple name Tirupati rejection)
        st1, res1 = http_req("GET", "/api/full-status/InvalidTempleName?hour=10&day_of_week=Monday&is_weekend=0&is_holiday=0&is_festival=0&weather=Sunny&temperature=30&previous_visitors=100")
        st2, res2 = http_req("GET", "/api/full-status/Tirupati?hour=10&day_of_week=Monday&is_weekend=0&is_holiday=0&is_festival=0&weather=Sunny&temperature=30&previous_visitors=100")
        if st1 == 404 and st2 == 404:
            print("  [OK] Invalid temple and old decommissioned temple rejected with 404 Not Found")
        else:
            self.log_issue(f"Expected 404 for invalid/old temple, got {st1}, {st2}")

        # B. Invalid demo scenario
        st, res = http_req("GET", "/api/demo/non-existent-scenario")
        if st == 404:
            print("  [OK] Invalid demo scenario rejected with 404 Not Found")
        else:
            self.log_issue(f"Expected 404 for invalid demo scenario, got {st}")

        # C. Invalid incident ID
        st, res = http_req("POST", "/api/incidents/NON-EXISTENT-ID/acknowledge")
        if st == 404:
            print("  [OK] Invalid incident ID rejected with 404 Not Found")
        else:
            self.log_issue(f"Expected 404 for invalid incident ID, got {st}")

        # D. Invalid weather parameter
        st, res = http_req("GET", "/api/predict/Somnath?hour=10&day_of_week=Wednesday&is_weekend=0&is_holiday=0&is_festival=0&weather=TornadoStorm&temperature=30&previous_visitors=3000&current_crowd=8000")
        if st == 400:
            print("  [OK] Invalid weather category rejected with 400 Bad Request")
        else:
            self.log_issue(f"Expected 400 for invalid weather, got {st}")

    # ------------------------------------------------------------------------
    # 6. DASHBOARD DATA CONTRACT VALIDATION
    # ------------------------------------------------------------------------
    def test_dashboard_data_contract(self):
        print("\n" + "=" * 80)
        print(">> [6/6] GOVERNMENT DASHBOARD JSON CONTRACT VALIDATION")
        print("=" * 80)

        st, data = http_req("GET", "/api/demo/emergency-overcrowding")
        contract_valid = True

        required_keys = [
            ("temple", str),
            ("timestamp", str),
            ("zones", list),
            ("intelligence", dict),
            ("resource_recommendations", dict),
            ("operations", dict),
            ("emergency_priority", str),
            ("reasoning", list),
        ]

        for k, t in required_keys:
            if k not in data or not isinstance(data[k], t):
                self.log_issue(f"Contract error: Missing/invalid top-level key '{k}' of type {t}")
                contract_valid = False

        # Validate nested intelligence contract
        intel = data.get("intelligence", {})
        if "crowd_intelligence" not in intel or "final_crowd_score" not in intel["crowd_intelligence"]:
            self.log_issue("Contract error: missing crowd_intelligence in payload")
            contract_valid = False

        if "ai_prediction" not in intel or "predicted_visitors" not in intel["ai_prediction"]:
            self.log_issue("Contract error: missing ai_prediction in payload")
            contract_valid = False

        if "live_data" not in intel or "average_density" not in intel["live_data"]:
            self.log_issue("Contract error: missing live_data in payload")
            contract_valid = False

        # Validate zones array contract
        zones = data.get("zones", [])
        if len(zones) != 4:
            self.log_issue(f"Contract error: expected 4 zone records, found {len(zones)}")
            contract_valid = False

        for z in zones:
            for zk, zt in [("zone", str), ("crowd_density", (int, float)), ("current_people", int), ("risk_level", str)]:
                if zk not in z or not isinstance(z[zk], zt):
                    self.log_issue(f"Contract error: zone missing {zk}")
                    contract_valid = False

        if contract_valid:
            self.results["integration"]["Dashboard Data Contract"] = True
            print("  [OK] Dashboard JSON schema and data contracts 100% verified.")
        else:
            self.results["integration"]["Dashboard Data Contract"] = False

    # ------------------------------------------------------------------------
    # 7. PRINT FINAL REPORT
    # ------------------------------------------------------------------------
    def print_final_report(self):
        print("\n" + "=" * 52)
        print("YATRASAFE FINAL INTEGRATION TEST REPORT")
        print("=" * 52)

        print("\nSYSTEM COMPONENTS:")
        for name, passed in self.results["components"].items():
            status_str = "[PASS]" if passed else "[FAIL]"
            print(f"{status_str} {name}")

        print("\nDEMO SCENARIOS:")
        for name, passed in self.results["scenarios"].items():
            status_str = "[PASS]" if passed else "[FAIL]"
            print(f"{status_str} {name}")

        print("\nINTEGRATION:")
        for name, passed in self.results["integration"].items():
            status_str = "[PASS]" if passed else "[FAIL]"
            print(f"{status_str} {name}")

        all_passed = (
            all(self.results["components"].values())
            and all(self.results["scenarios"].values())
            and all(self.results["integration"].values())
            and len(self.results["issues"]) == 0
        )

        print("\nFINAL STATUS:")
        if all_passed:
            print("READY FOR HACKATHON")
        else:
            print("ISSUES FOUND:")
            for iss in self.results["issues"]:
                print(f"  - {iss}")
        print("=" * 52)
        return all_passed


if __name__ == "__main__":
    tester = EndToEndTester()
    tester.test_system_health()
    tester.test_api_endpoints()
    tester.test_demo_scenarios()
    tester.test_cross_module_consistency()
    tester.test_error_handling()
    tester.test_dashboard_data_contract()
    success = tester.print_final_report()
    sys.exit(0 if success else 1)
