# 🏆 YatraSafe AI + Real-Time Module: Hackathon Demo & Presentation Guide

> **Project**: YatraSafe - AI-Powered Crowd Intelligence, Real-Time IoT Telemetry & Incident Decision Support for Gujarat Pilgrimage Shrines.

---

## 1. 📌 Project Overview & End-to-End Intelligence Flow

**YatraSafe** is an intelligent crowd safety and capacity management platform built to prevent stampedes, dangerous bottleneck crushes, and severe queue delays across Gujarat's 4 major pilgrimage destinations:
- **Somnath** (1st Jyotirlinga, Saurashtra coast)
- **Dwarka** (Dwarkadhish Temple, Char Dham)
- **Ambaji** (Major Shakti Peeth on Arasur hill)
- **Pavagadh** (Kalika Mata hilltop Shakti Peeth)

### The Complete Intelligence Architecture Flow:

```text
  ┌───────────────────────────────┐     ┌────────────────────────────────┐
  │     Historical Crowd Data     │     │   Live IoT Multi-Zone Feeds    │
  │ (14,400 Hourly Gujarat Records│     │  (Gates, Queues, Entrance, Pkg)│
  └───────────────┬───────────────┘     └───────────────┬────────────────┘
                  │                                     │
                  ▼                                     ▼
  ┌───────────────────────────────┐     ┌────────────────────────────────┐
  │  Temporal / Weather Context   │     │   Live Accumulation & Dwell    │
  │ (Hour, Festival, Day, Temp)   │     │  (Density %, Inflow, Outflow)  │
  └───────────────┬───────────────┘     └───────────────┬────────────────┘
                  │                                     │
                  ▼                                     │
  ┌───────────────────────────────┐                     │
  │      AI Prediction Engine     │                     │
  │ (RandomForest Inflow Forecast)│                     │
  └───────────────┬───────────────┘                     │
                  │ (40% Weight)                        │ (60% Weight)
                  └───────────────┬─────────────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │   Crowd Intelligence Engine   │
                  │  (Score, Trend, Zone Alerts)  │
                  └───────────────┬───────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │ Smart Resource Recommendation │
                  │ (Security, Medical, Gates)    │
                  └───────────────┬───────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │   Incident Command & Admin    │
                  │ (Govt / Temple Control Panel) │
                  └───────────────────────────────┘
```

---

## 2. ⚡ Pre-Demo Setup (Windows Quickstart)

To run the live interactive presentation, open **two separate PowerShell terminals**:

### Terminal 1: Real-Time IoT Sensor Simulator
```powershell
cd ai-realtime
.\.venv\Scripts\activate
python realtime/sensor_simulator.py
```
> *Starts live stateful IoT telemetry generation across the 4 Gujarat shrines, saving state every 3 seconds to `realtime/latest_sensor_data.json`.*

### Terminal 2: FastAPI Prediction & Resource Microservice
```powershell
cd ai-realtime
.\.venv\Scripts\activate
python -m uvicorn api.prediction_api:app --host 127.0.0.1 --port 8000
```
> *Launches the RESTful API microservice on `http://127.0.0.1:8000`.*

### Dashboards & Swagger UI
- **Government Command Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 3. 🎬 Demo Scenario Presentation Sequence

Demonstrate the safety progression from **LOW** to **CRITICAL** in this exact order:

```text
       🟢 LOW        ───►     🟡 MODERATE    ───►      🟠 HIGH       ───►     🔴 CRITICAL
     (Normal Day)           (Busy Weekend)          (Festival Rush)       (Emergency Overcrowding)
       Somnath                  Dwarka                  Ambaji                   Pavagadh
```

---

### Scenario 1: Normal Day Operations (🟢 LOW Risk)
* **API Endpoint**: `GET /api/demo/normal-day`
* **Temple**: Somnath (Wednesday 10:00 AM)
* **Expected Metrics**:
  - **Crowd Score**: ~`22.4%` (`LOW`)
  - **Security Allocation**: `2 units`
  - **Medical Personnel**: `1 unit`
  - **Additional Gates**: `0`
  - **Emergency Priority**: `LOW`
* **Operational Directive**: *"Normal operations. Continue routine monitoring."*

---

### Scenario 2: Busy Weekend Darshan (🟡 MODERATE Risk)
* **API Endpoint**: `GET /api/demo/busy-weekend`
* **Temple**: Dwarka (Saturday 8:00 AM)
* **Expected Metrics**:
  - **Crowd Score**: ~`65.9%` (`MODERATE`)
  - **Security Allocation**: `4 units`
  - **Medical Personnel**: `1 unit`
  - **Additional Gates**: `+1 additional gate`
  - **Emergency Priority**: `MODERATE`
* **Operational Directive**: *"Increase monitoring and prepare additional queue and security resources."*

---

### Scenario 3: Major Festival Surge (🟠 HIGH Risk)
* **API Endpoint**: `GET /api/demo/festival-rush`
* **Temple**: Ambaji (Sunday 6:00 PM, Festival Evening)
* **Expected Metrics**:
  - **Crowd Score**: ~`84.4%` (`HIGH`)
  - **Security Allocation**: `8 units`
  - **Medical Personnel**: `2 units`
  - **Additional Gates**: `+2 additional gates`
  - **Emergency Priority**: `HIGH`
* **Operational Directive**: *"Deploy additional security staff, activate alternate queue routing, and closely monitor high-density zones."*

---

### Scenario 4: Critical Overcrowding & Emergency Alert (🔴 CRITICAL Risk)
* **API Endpoint**: `GET /api/demo/emergency-overcrowding`
* **Temple**: Pavagadh (Sunday 5:00 PM, Hilltop Surge)
* **Expected Metrics**:
  - **Crowd Score**: ~`86.6%` (`CRITICAL`)
  - **Security Allocation**: `20 units` (15 base + 2 surge + 3 bottleneck intervention)
  - **Medical Personnel**: `4 units`
  - **Additional Gates**: `+3 emergency gates`
  - **Emergency Priority**: `CRITICAL`
  - **Active Zone Alerts**: **4 CRITICAL alerts** (`Main Gate: 92%`, `Darshan Queue: 95%`, `Temple Entrance: 94%`, `Parking: 90%`)
  - **Parking Action**: *"Redirect incoming vehicles to alternate parking."*
* **Incident Command Center Action**: Automatically opens 4 critical incident dispatch tickets for command operator acknowledgment and resolution.
