"""
FastAPI Microservice for TirthaSetu AI + Real-Time Crowd Intelligence & Resource Allocation.

Exposes RESTful endpoints for health checks, temple catalogs, live sensor telemetry,
AI predictive analytics, unified crowd intelligence diagnostics, automated smart
resource recommendations, and Hackathon interactive demo scenarios.
"""

import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

# Ensure project root is available in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DASHBOARD_HTML_PATH = os.path.join(PROJECT_ROOT, "dashboard", "index.html")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.analytics import analytics_manager
from api.incidents import incident_manager
from crowd_engine.crowd_engine import (
    analyze_temple,
    load_live_sensor_data,
)
from demo.demo_scenarios import (
    DEMO_SCENARIOS,
    run_demo_scenario,
)
from ml.predict import (
    SUPPORTED_TEMPLES,
    SUPPORTED_WEATHER,
    predict_crowd,
)
from resource_engine.resource_recommender import (
    recommend_resources,
)

# Initialize FastAPI application with OpenAPI/Swagger metadata
app = FastAPI(
    title="TirthaSetu AI + Real-Time Prediction & Resource API",
    description=(
        "Production-grade REST microservice providing AI crowd predictions, "
        "live IoT multi-zone sensor feeds, unified Crowd Intelligence analytics, "
        "automated smart operational resource recommendations, and interactive "
        "Hackathon Demo Scenarios for pilgrimage temples."
    ),
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# The standalone ML dashboard is served by this app. React uses the Node gateway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ML_ALLOWED_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000").split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Government Dashboard"],
    summary="Government Command Dashboard Portal",
    description="Serves the interactive TirthaSetu Pilgrim Safety & Crowd Command Dashboard UI.",
    include_in_schema=False,
)
@app.get(
    "/dashboard",
    tags=["Government Dashboard"],
    summary="Government Command Dashboard Portal",
    description="Serves the interactive TirthaSetu Pilgrim Safety & Crowd Command Dashboard UI.",
)
async def serve_dashboard():
    """Serve the interactive Government Command Dashboard web interface."""
    if os.path.exists(DASHBOARD_HTML_PATH):
        return FileResponse(DASHBOARD_HTML_PATH, media_type="text/html")
    return HTMLResponse("<h1>TirthaSetu Government Dashboard</h1><p>Dashboard HTML not found.</p>")


@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Returns the operational status and service identification name.",
)
async def health_check():
    """Service health verification endpoint."""
    return {
        "status": "healthy",
        "service": "TirthaSetu AI + Real-Time Service",
    }


@app.get(
    "/api/temples",
    tags=["Metadata"],
    summary="List Supported Temples",
    description="Returns the list of all pilgrimage temples supported by the AI module.",
)
async def get_temples():
    """Retrieve all supported temple destinations."""
    return {
        "temples": SUPPORTED_TEMPLES,
    }


@app.get(
    "/api/realtime/{temple}",
    tags=["Real-Time Telemetry"],
    summary="Get Real-Time Sensor Telemetry",
    description="Retrieves the latest live IoT sensor records and aggregate metrics for a specific temple.",
)
async def get_realtime_sensor_data(temple: str):
    """Retrieve latest live sensor snapshot for a given temple."""
    if temple not in SUPPORTED_TEMPLES:
        raise HTTPException(
            status_code=404,
            detail=f"Temple '{temple}' is not supported. Supported temples are: {SUPPORTED_TEMPLES}",
        )

    try:
        snapshot = load_live_sensor_data()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Sensor data feed is not currently active. Start the realtime sensor simulator.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading sensor snapshot: {str(exc)}",
        )

    sensors = snapshot.get("sensors", [])
    temple_zones = [s for s in sensors if s.get("temple") == temple]

    if not temple_zones:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry records found for temple '{temple}'.",
        )

    # Compute summary metrics
    non_parking = [z for z in temple_zones if z.get("zone") != "Parking"]
    parking = next((z for z in temple_zones if z.get("zone") == "Parking"), None)

    all_densities = [float(z.get("crowd_density", 0.0)) for z in temple_zones]
    avg_density = round(sum(all_densities) / len(all_densities), 2) if all_densities else 0.0
    max_density = round(max(all_densities), 2) if all_densities else 0.0
    total_people = sum(int(z.get("current_people", 0)) for z in non_parking)
    parking_occ = (
        round(float(parking.get("parking_occupancy", 0.0)), 2)
        if parking and parking.get("parking_occupancy") is not None
        else 0.0
    )

    return {
        "temple": temple,
        "timestamp": snapshot.get("timestamp"),
        "zones": temple_zones,
        "summary": {
            "average_density": avg_density,
            "max_density": max_density,
            "total_current_people": total_people,
            "parking_occupancy": parking_occ,
        },
    }


@app.get(
    "/api/predict/{temple}",
    tags=["AI Prediction Engine"],
    summary="Predict Temple Crowd Inflow",
    description="Generates an ML-driven visitor arrival forecast and capacity saturation risk evaluation.",
)
async def predict_temple_crowd(
    temple: str,
    hour: int = Query(..., ge=0, le=23, description="Hour of the day (0-23)"),
    day_of_week: str = Query(..., description="Day of the week (e.g., Monday, Saturday)"),
    is_weekend: int = Query(..., ge=0, le=1, description="1 if Saturday/Sunday, else 0"),
    is_holiday: int = Query(..., ge=0, le=1, description="1 if public holiday, else 0"),
    is_festival: int = Query(..., ge=0, le=1, description="1 if religious festival, else 0"),
    weather: str = Query(..., description="Weather condition (Sunny, Cloudy, Rainy, Clear, Heavy Rain)"),
    temperature: float = Query(..., description="Temperature in Celsius"),
    previous_visitors: int = Query(..., ge=0, description="Visitor inflow in the previous hour"),
    current_crowd: int = Query(..., ge=0, description="Active crowd accumulation in temple complex"),
):
    """Execute AI ML prediction for temple crowd flow."""
    if temple not in SUPPORTED_TEMPLES:
        raise HTTPException(
            status_code=404,
            detail=f"Temple '{temple}' is not supported. Supported temples: {SUPPORTED_TEMPLES}",
        )

    if weather not in SUPPORTED_WEATHER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid weather '{weather}'. Allowed values: {SUPPORTED_WEATHER}",
        )

    try:
        result = predict_crowd(
            temple=temple,
            hour=hour,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            is_festival=is_festival,
            weather=weather,
            temperature=temperature,
            previous_visitors=previous_visitors,
            current_crowd=current_crowd,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI Prediction Engine error: {str(exc)}",
        )


@app.get(
    "/api/intelligence/{temple}",
    tags=["Crowd Intelligence"],
    summary="Unified Crowd Intelligence Analysis",
    description=(
        "Fuses ML predictive modeling (40%) with live multi-zone IoT sensor telemetry (60%) "
        "to calculate unified crowd scores, directional flow trends, and operational response alerts."
    ),
)
async def get_temple_crowd_intelligence(
    temple: str,
    hour: int = Query(..., ge=0, le=23, description="Hour of the day (0-23)"),
    day_of_week: str = Query(..., description="Day of the week (e.g., Monday, Saturday)"),
    is_weekend: int = Query(..., ge=0, le=1, description="1 if Saturday/Sunday, else 0"),
    is_holiday: int = Query(..., ge=0, le=1, description="1 if public holiday, else 0"),
    is_festival: int = Query(..., ge=0, le=1, description="1 if religious festival, else 0"),
    weather: str = Query(..., description="Weather condition (Sunny, Cloudy, Rainy, Clear, Heavy Rain)"),
    temperature: float = Query(..., description="Temperature in Celsius"),
    previous_visitors: int = Query(..., ge=0, description="Visitor inflow in previous hour"),
):
    """Execute unified Crowd Intelligence analysis combining AI and Live Sensors."""
    if temple not in SUPPORTED_TEMPLES:
        raise HTTPException(
            status_code=404,
            detail=f"Temple '{temple}' is not supported. Supported temples: {SUPPORTED_TEMPLES}",
        )

    if weather not in SUPPORTED_WEATHER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid weather '{weather}'. Allowed values: {SUPPORTED_WEATHER}",
        )

    try:
        analysis = analyze_temple(
            temple=temple,
            hour=hour,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            is_festival=is_festival,
            weather=weather,
            temperature=temperature,
            previous_visitors=previous_visitors,
        )
        return analysis
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Live sensor telemetry stream is not available. Please run sensor_simulator.py.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Crowd Intelligence Engine error: {str(exc)}",
        )


@app.get(
    "/api/recommendations/{temple}",
    tags=["Resource Recommendation Engine"],
    summary="Generate Smart Resource Recommendations",
    description=(
        "Converts fused crowd intelligence diagnostics into real-time operational resource allocations "
        "for security staff, medical response teams, gate operations, and queue routing."
    ),
)
async def get_temple_resource_recommendations(
    temple: str,
    hour: int = Query(..., ge=0, le=23, description="Hour of the day (0-23)"),
    day_of_week: str = Query(..., description="Day of the week (e.g., Monday, Saturday)"),
    is_weekend: int = Query(..., ge=0, le=1, description="1 if Saturday/Sunday, else 0"),
    is_holiday: int = Query(..., ge=0, le=1, description="1 if public holiday, else 0"),
    is_festival: int = Query(..., ge=0, le=1, description="1 if religious festival, else 0"),
    weather: str = Query(..., description="Weather condition (Sunny, Cloudy, Rainy, Clear, Heavy Rain)"),
    temperature: float = Query(..., description="Temperature in Celsius"),
    previous_visitors: int = Query(..., ge=0, description="Visitor inflow in previous hour"),
):
    """Generate smart resource allocation recommendations for a temple."""
    if temple not in SUPPORTED_TEMPLES:
        raise HTTPException(
            status_code=404,
            detail=f"Temple '{temple}' is not supported. Supported temples: {SUPPORTED_TEMPLES}",
        )

    if weather not in SUPPORTED_WEATHER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid weather '{weather}'. Allowed values: {SUPPORTED_WEATHER}",
        )

    try:
        # Step 1: Run Crowd Intelligence analysis
        intelligence_result = analyze_temple(
            temple=temple,
            hour=hour,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            is_festival=is_festival,
            weather=weather,
            temperature=temperature,
            previous_visitors=previous_visitors,
        )

        # Step 2: Convert intelligence diagnostics into operational recommendations
        recommendations = recommend_resources(intelligence_result)
        return recommendations
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Live sensor telemetry snapshot not found. Please start sensor_simulator.py.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Resource Recommendation Engine error: {str(exc)}",
        )


@app.get(
    "/api/full-status/{temple}",
    tags=["Unified Diagnostics"],
    summary="Get Complete Temple Status & Resource Directives",
    description=(
        "Single comprehensive endpoint returning AI inflow forecasts, live multi-zone sensor telemetry, "
        "fused crowd intelligence metrics, directional trends, zone alerts, and automated resource allocations."
    ),
)
async def get_temple_full_status(
    temple: str,
    hour: int = Query(..., ge=0, le=23, description="Hour of the day (0-23)"),
    day_of_week: str = Query(..., description="Day of the week (e.g., Monday, Saturday)"),
    is_weekend: int = Query(..., ge=0, le=1, description="1 if Saturday/Sunday, else 0"),
    is_holiday: int = Query(..., ge=0, le=1, description="1 if public holiday, else 0"),
    is_festival: int = Query(..., ge=0, le=1, description="1 if religious festival, else 0"),
    weather: str = Query(..., description="Weather condition (Sunny, Cloudy, Rainy, Clear, Heavy Rain)"),
    temperature: float = Query(..., description="Temperature in Celsius"),
    previous_visitors: int = Query(..., ge=0, description="Visitor inflow in previous hour"),
):
    """Retrieve full unified diagnosis: AI Forecast + Live Telemetry + Intelligence + Resource Action Plan."""
    if temple not in SUPPORTED_TEMPLES:
        raise HTTPException(
            status_code=404,
            detail=f"Temple '{temple}' is not supported. Supported temples: {SUPPORTED_TEMPLES}",
        )

    if weather not in SUPPORTED_WEATHER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid weather '{weather}'. Allowed values: {SUPPORTED_WEATHER}",
        )

    try:
        # Step 1: Perform unified crowd intelligence analysis
        intelligence_result = analyze_temple(
            temple=temple,
            hour=hour,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            is_festival=is_festival,
            weather=weather,
            temperature=temperature,
            previous_visitors=previous_visitors,
        )

        # Step 2: Generate resource recommendations from intelligence result
        resource_result = recommend_resources(intelligence_result)

        # Step 3: Synchronize active zone alerts with Incident Command Center
        alerts = intelligence_result.get("alerts", [])
        if alerts:
            incident_manager.sync_from_alerts(alerts, temple)

        # Step 4: Record analytics snapshot
        analytics_manager.record_snapshot(
            temple=intelligence_result["temple"],
            crowd_score=intelligence_result["crowd_intelligence"]["final_crowd_score"],
            risk_level=intelligence_result["crowd_intelligence"]["final_risk_level"],
            trend=intelligence_result["crowd_intelligence"]["trend"],
            live_average_density=intelligence_result["live_data"]["average_density"],
            max_zone_density=intelligence_result["live_data"]["max_zone_density"],
            highest_risk_zone=intelligence_result["live_data"]["highest_risk_zone"],
            predicted_visitors=intelligence_result["ai_prediction"]["predicted_visitors"],
        )

        # Step 5: Package clean, non-duplicated unified response payload
        return {
            "temple": intelligence_result["temple"],
            "timestamp": intelligence_result["timestamp"],
            "zones": intelligence_result.get("zones", intelligence_result["live_data"].get("zones", [])),
            "intelligence": {
                "ai_prediction": intelligence_result["ai_prediction"],
                "live_data": intelligence_result["live_data"],
                "crowd_intelligence": intelligence_result["crowd_intelligence"],
                "alerts": intelligence_result["alerts"],
            },
            "resource_recommendations": resource_result["resource_recommendations"],
            "operations": resource_result["operations"],
            "emergency_priority": resource_result["emergency_priority"],
            "reasoning": resource_result["reasoning"],
        }
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Live sensor telemetry snapshot not found. Please start sensor_simulator.py.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Full status generation error: {str(exc)}",
        )


# ============================================================================
# ANALYTICS & DECISION INSIGHTS ENDPOINTS
# ============================================================================

@app.get(
    "/api/analytics/summary",
    tags=["Analytics & Decision Insights"],
    summary="Get Executive Analytics Summary",
    description="Calculates average crowd score, highest-risk temple, most affected zone, risk distribution, and incident aggregates.",
)
async def get_analytics_summary():
    """Retrieve executive decision insights and KPI aggregates."""
    return analytics_manager.get_summary()


@app.get(
    "/api/analytics/trends",
    tags=["Analytics & Decision Insights"],
    summary="Get Historical Crowd Trends",
    description="Retrieves time-series telemetry snapshots across temples for trend graphing.",
)
async def get_analytics_trends(
    limit: int = Query(30, ge=5, le=100, description="Number of historical snapshot points to return"),
):
    """Retrieve chronological trend data for charting."""
    return analytics_manager.get_trends(limit=limit)


@app.get(
    "/api/analytics/risk-distribution",
    tags=["Analytics & Decision Insights"],
    summary="Get Safety Risk Distribution",
    description="Returns count and percentage breakdown across LOW, MODERATE, HIGH, and CRITICAL risk tiers.",
)
async def get_risk_distribution():
    """Retrieve safety tier distribution."""
    return analytics_manager.get_risk_distribution()


@app.get(
    "/api/analytics/temple-comparison",
    tags=["Analytics & Decision Insights"],
    summary="Compare Multi-Temple Status",
    description="Comparative analysis across all 4 supported pilgrimage sites showing current crowd scores, risk levels, and peak zone saturation.",
)
async def get_temple_comparison():
    """Retrieve side-by-side temple comparison dataset."""
    return analytics_manager.get_temple_comparison()


@app.get(
    "/api/analytics/incidents",
    tags=["Analytics & Decision Insights"],
    summary="Get Incident Analytics & Breakdown",
    description="Aggregates incidents by temple, affected zone, and severity tier.",
)
async def get_incident_analytics():
    """Retrieve incident breakdown analytics."""
    return analytics_manager.get_incident_analytics()


# ============================================================================
# INCIDENT COMMAND CENTER ENDPOINTS
# ============================================================================

@app.get(
    "/api/incidents/active",
    tags=["Incident Command Center"],
    summary="Get Active Safety Incidents",
    description="Retrieves all currently active and acknowledged crowd safety incidents across pilgrimage temples.",
)
async def get_active_incidents(
    temple: Optional[str] = Query(None, description="Filter incidents by temple name"),
):
    """Retrieve active and acknowledged crowd incidents."""
    incidents = incident_manager.get_active_incidents(temple=temple)
    return {
        "total_active": len(incidents),
        "incidents": incidents,
    }


@app.get(
    "/api/incidents/history",
    tags=["Incident Command Center"],
    summary="Get Incident Audit History",
    description="Retrieves chronological audit log of all safety incidents (active, acknowledged, and resolved).",
)
async def get_incident_history(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of historical records to return"),
):
    """Retrieve chronological incident audit logs."""
    history = incident_manager.get_incident_history(limit=limit)
    return {
        "total_history": len(history),
        "incidents": history,
    }


@app.post(
    "/api/incidents/{incident_id}/acknowledge",
    tags=["Incident Command Center"],
    summary="Acknowledge Safety Incident",
    description="Marks an active incident as ACKNOWLEDGED by the government command operator.",
)
async def acknowledge_incident(incident_id: str):
    """Acknowledge a critical crowd safety incident."""
    inc = incident_manager.acknowledge_incident(incident_id)
    if not inc:
        raise HTTPException(
            status_code=404,
            detail=f"Incident with ID '{incident_id}' not found.",
        )
    return {
        "status": "success",
        "message": f"Incident {incident_id} successfully acknowledged.",
        "incident": inc,
    }


@app.post(
    "/api/incidents/{incident_id}/resolve",
    tags=["Incident Command Center"],
    summary="Resolve Safety Incident",
    description="Marks an incident as RESOLVED following on-ground crowd relief operations.",
)
async def resolve_incident(incident_id: str):
    """Resolve an incident and mark relief completed."""
    inc = incident_manager.resolve_incident(incident_id)
    if not inc:
        raise HTTPException(
            status_code=404,
            detail=f"Incident with ID '{incident_id}' not found.",
        )
    return {
        "status": "success",
        "message": f"Incident {incident_id} successfully resolved.",
        "incident": inc,
    }


@app.get(
    "/api/demo/scenarios",
    tags=["Hackathon Demo System"],
    summary="List Available Demo Scenarios",
    description="Returns metadata and descriptions for all controlled hackathon demo scenarios (LOW -> MODERATE -> HIGH -> CRITICAL).",
)
async def list_demo_scenarios():
    """Retrieve catalog of all 4 pre-configured demo scenarios."""
    scenarios_list = [
        {
            "name": cfg["slug"],
            "title": cfg["title"],
            "description": cfg["description"],
            "temple": cfg["temple"],
        }
        for cfg in DEMO_SCENARIOS.values()
    ]
    return {
        "total_scenarios": len(scenarios_list),
        "scenarios": scenarios_list,
    }


@app.get(
    "/api/demo/{scenario_name}",
    tags=["Hackathon Demo System"],
    summary="Execute Demo Scenario",
    description=(
        "Executes a deterministic crowd situation through the real AI & Resource pipeline. "
        "Supported scenario names: 'normal-day', 'busy-weekend', 'festival-rush', 'emergency-overcrowding'."
    ),
)
async def run_demo(scenario_name: str):
    """Execute a specified demo scenario and return full diagnostic report."""
    normalized_name = scenario_name.strip().lower().replace("_", "-")
    if normalized_name not in DEMO_SCENARIOS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown demo scenario '{scenario_name}'. "
                f"Supported scenario names: {list(DEMO_SCENARIOS.keys())}"
            ),
        )

    try:
        result = run_demo_scenario(normalized_name)
        # Sync demo alerts into Incident Command Center
        demo_alerts = result.get("intelligence", {}).get("alerts", [])
        if demo_alerts:
            incident_manager.sync_from_alerts(demo_alerts, result["temple"])

        # Record demo snapshot in Analytics Engine
        analytics_manager.record_snapshot(
            temple=result["temple"],
            crowd_score=result["intelligence"]["crowd_intelligence"]["final_crowd_score"],
            risk_level=result["intelligence"]["crowd_intelligence"]["final_risk_level"],
            trend=result["intelligence"]["crowd_intelligence"]["trend"],
            live_average_density=result["intelligence"]["live_data"]["average_density"],
            max_zone_density=result["intelligence"]["live_data"]["max_zone_density"],
            highest_risk_zone=result["intelligence"]["live_data"]["highest_risk_zone"],
            predicted_visitors=result["intelligence"]["ai_prediction"]["predicted_visitors"],
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing demo scenario '{scenario_name}': {str(exc)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("prediction_api:app", host="127.0.0.1", port=8000, reload=False)
