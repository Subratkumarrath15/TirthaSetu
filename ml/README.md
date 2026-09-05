# TirthaSetu AI + Real-Time Intelligence Module (Gujarat Shrines)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9.0-orange.svg?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Hackathon%20Ready-brightgreen.svg)]()

> **Part of the TirthaSetu Platform**: An AI-powered crowd safety, real-time IoT sensor telemetry, predictive analytics, and automated resource allocation system for Gujarat pilgrimage shrines and high-density religious gatherings.

---

## 📌 Module Purpose

The **TirthaSetu AI + Real-Time Intelligence Module** serves as the analytical brain of the TirthaSetu ecosystem. It bridges the gap between historical pilgrim trends and real-time physical conditions across Gujarat's most prominent pilgrimage sites:
1. **Forecasting hourly pilgrim inflows and capacity risks** using a trained Random Forest Regressor ($R^2 = 0.9808$, $\text{MAE} = 97.53$).
2. **Simulating live multi-zone IoT sensor telemetry** (`Main Gate`, `Darshan Queue`, `Temple Entrance`, `Parking`) across 4 Gujarat pilgrimage destinations:
   - **Somnath** (Capacity: 40,000)
   - **Dwarka** (Capacity: 35,000)
   - **Ambaji** (Capacity: 50,000)
   - **Pavagadh** (Capacity: 25,000)
3. **Fusing predictive forecasts (40% weight) with live sensor observations (60% weight)** to generate unified crowd scores and flow trends (`RISING`, `FALLING`, `STABLE`).
4. **Generating dynamic, automated operational resource allocations** (security personnel, medical response units, additional gates, queue rerouting, and parking diversions).
5. **Managing active incident lifecycles** (Incident Command Center) with acknowledge/resolve state machines.
6. **Aggregating decision analytics** (time-series trends, risk tier distributions, and multi-shrine comparison matrix).
7. **Exposing clean RESTful microservices** and hosting the dark-mode Government Command Dashboard.

---

## 🏛️ System Architecture

```text
       Historical Crowd Dataset (14,400 Records)
                           +
        Festival / Weather / Weekend / Time Features
                           ↓
     Machine Learning Prediction Pipeline (Random Forest)
                           +
       Stateful Multi-Zone IoT Sensor Telemetry (4 Zones)
                           ↓
             Crowd Intelligence Engine
         [40% AI Forecast + 60% Live Telemetry]
                           ↓
         Safety Risk Tier + Trend Direction + Zone Alerts
                           ↓
          Smart Resource Recommendation Engine
     [Security Units, Medical Teams, Gates, Queue Routing]
                           ↓
           Alert & Incident Command Center
          [Acknowledge, Resolve, Audit Tracking]
                           ↓
            Analytics & Decision Insights
         [Longitudinal Trends, Risk Breakdown, Cross-Shrine Matrix]
                           ↓
          Government Command & Control Dashboard
```

---

## 📁 Folder Structure

```text
ai-realtime/
├── data/
│   ├── generate_dataset.py          # Synthetic dataset generator for 4 Gujarat shrines
│   ├── historical_crowd.csv         # 14,400 rows of validated historical crowd metrics
│   └── inspect_dataset.py           # Dataset validation & statistical integrity suite
├── models/
│   ├── crowd_model.pkl              # Trained ML pipeline (OneHotEncoder + RandomForest)
│   └── model_metrics.json           # Evaluation metrics (R²: 0.9808, MAE: 97.53)
├── ml/
│   ├── train.py                     # Offline ML model training pipeline
│   └── predict.py                   # Standalone AI inference & capacity risk engine
├── realtime/
│   ├── sensor_simulator.py          # Stateful multi-zone IoT sensor simulator (4 shrines)
│   └── latest_sensor_data.json      # Live JSON snapshot updated every 3 seconds
├── crowd_engine/
│   ├── __init__.py
│   └── crowd_engine.py              # Fuses AI predictions (40%) and live sensors (60%)
├── resource_engine/
│   ├── __init__.py
│   └── resource_recommender.py      # Automated security, medical, and gate allocator
├── api/
│   ├── prediction_api.py            # FastAPI REST microservice + Dashboard routes
│   ├── incidents.py                 # Incident Command Center manager
│   ├── analytics.py                 # Analytics & Decision Insights engine
│   └── test_*.py                    # Verification test suites
├── dashboard/
│   ├── index.html                   # Government Command Dashboard UI
│   └── GovernmentDashboard.jsx      # React component mirror
├── demo/
│   ├── demo_scenarios.py            # 4 controlled hackathon demo scenarios
│   ├── test_end_to_end.py           # Master end-to-end integration test
│   └── HACKATHON_DEMO_GUIDE.md      # Step-by-step presentation runbook
├── docs/
│   ├── PROJECT_OVERVIEW.md          # Comprehensive executive overview
│   ├── PRESENTATION_SCRIPT.md       # Timed pitches, script, and judge Q&A
│   └── FINAL_DEMO_CHECKLIST.md      # Pre-demo and during-demo checklist
└── start_tirthasetu.bat              # One-click Windows application launcher
```

---

## 🚀 Quick Start Guide

### 1. Windows Virtual Environment Setup
```powershell
cd ai-realtime
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Dataset Generation & ML Training
```powershell
python data/generate_dataset.py
python ml/train.py
```

### 3. Start IoT Telemetry Simulator
```powershell
python realtime/sensor_simulator.py
```

### 4. Start FastAPI Server
```powershell
python -m uvicorn api.prediction_api:app --host 127.0.0.1 --port 8000
```

### 5. Access Dashboards & APIs
- **Government Command Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Base URL**: `http://127.0.0.1:8000`

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Service health status check |
| **GET** | `/api/temples` | List of 4 supported Gujarat temples |
| **GET** | `/api/realtime/{temple}` | Live multi-zone sensor telemetry snapshot |
| **GET** | `/api/predict/{temple}` | AI crowd prediction & capacity risk |
| **GET** | `/api/intelligence/{temple}` | Unified 40/60 AI+IoT crowd intelligence |
| **GET** | `/api/recommendations/{temple}` | Smart resource allocations & directives |
| **GET** | `/api/full-status/{temple}` | Complete master operational diagnostic status |
| **GET** | `/api/demo/scenarios` | List available hackathon demo scenarios |
| **GET** | `/api/demo/normal-day` | Scenario 1: Somnath (`LOW` risk, ~22.4%) |
| **GET** | `/api/demo/busy-weekend` | Scenario 2: Dwarka (`MODERATE` risk, ~65.9%) |
| **GET** | `/api/demo/festival-rush` | Scenario 3: Ambaji (`HIGH` risk, ~84.4%) |
| **GET** | `/api/demo/emergency-overcrowding` | Scenario 4: Pavagadh (`CRITICAL` risk, ~86.6%, 4 alerts, 20 security units) |
| **GET** | `/api/incidents/active` | Active safety incidents |
| **GET** | `/api/incidents/history` | Audit log of all historical incidents |
| **POST** | `/api/incidents/{id}/acknowledge` | Acknowledge active incident |
| **POST** | `/api/incidents/{id}/resolve` | Resolve active incident |
| **GET** | `/api/analytics/summary` | Executive KPIs and overview summary |
| **GET** | `/api/analytics/trends` | Time-series crowd score snapshots |
| **GET** | `/api/analytics/risk-distribution` | Risk tier breakdown counts and percentages |
| **GET** | `/api/analytics/temple-comparison` | Cross-shrine comparative matrix (4 temples) |
| **GET** | `/api/analytics/incidents` | Incident breakdown analytics |

---

## 🧪 Verification & Testing

Run the master integration test suite:
```powershell
python demo/test_end_to_end.py
```
