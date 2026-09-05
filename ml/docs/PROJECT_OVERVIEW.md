# TirthaSetu: AI + Real-Time Pilgrim Safety Intelligence Platform
## Executive Project Overview & Architecture Guide (Gujarat Shrines)

---

### 📌 A. Problem Statement
Every year, tens of millions of devotees embark on pilgrimages across Gujarat's sacred destinations (*Somnath, Dwarka, Ambaji, and Pavagadh*). High-density religious gatherings frequently face severe crowd management challenges:
1. **Sudden Crowd Surges**: Unpredictable influxes caused by auspicious festival timings (Maha Shivratri at Somnath, Janmashtami at Dwarka, Bhadarvi Poonam at Ambaji, Navratri at Pavagadh), weather conditions, or weekend holidays.
2. **Zone Bottlenecks**: Extreme localized saturation in narrow sanctum queues (*Darshan Queue*) and hilltop ascent steps/ropeway stations (*Pavagadh*) while outer areas remain underutilized.
3. **Reactive vs. Proactive Deployment**: Police, security, and medical staff are typically dispatched *after* stampede conditions or overcrowding occur, rather than hours in advance.
4. **Information Silos**: Ground telemetry, weather forecasts, and historical crowd patterns are not unified into actionable government decision systems.

---

### 💡 B. The Solution
**TirthaSetu** is:
> *"An AI-powered real-time crowd intelligence and operational decision support platform for pilgrim safety."*

TirthaSetu unifies **Machine Learning arrival forecasting** with **real-time stateful IoT multi-zone sensor telemetry** across Gujarat's pilgrimage shrines to compute unified crowd safety scores, predict surge trajectories, trigger granular zone alarms, and automate government operational directives (security unit counts, medical teams, additional gate activations, queue routing, and vehicle diversions).

---

### 🏛️ C. Complete System Architecture

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

### 💻 D. Key Technologies

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** + **Uvicorn** | High-performance asynchronous microservice with Swagger OpenAPI specs |
| **Machine Learning** | **scikit-learn** (`RandomForestRegressor`) | Multi-feature visitor arrival prediction ($R^2 = 0.9808$, $\text{MAE} = 97.53$) |
| **Data Processing** | **pandas**, **NumPy**, **joblib** | Dataset feature engineering, encoding, and compressed pipeline serialization |
| **IoT Telemetry** | **Python Stateful Simulator** | Multi-zone inflow/outflow stochastic queue modeling across 4 Gujarat shrines |
| **Frontend Portal** | **HTML5**, **Tailwind CSS**, **Chart.js** | Dark-mode government operations portal with real-time Chart.js visual analytics |
| **Component Mirror** | **React / JSX** | Decoupled modern frontend component ready for production dashboard suites |
| **Integration** | **RESTful JSON APIs** | Clean CORS-enabled interfaces for cross-team consumption |

---

### 🚀 E. Core Innovations

1. **AI + Live Sensor Fusion (40/60 Weighted Intelligence)**:
   - Combines long-range predictive foresight ($40\%$ AI inflow forecast) with immediate ground reality ($60\%$ live multi-zone sensor density) to generate a robust Unified Safety Score.
2. **Explainable Crowd Risk Decisions**:
   - Every resource directive and risk level is accompanied by a transparent algorithmic audit trail detailing why specific security units and gates were allocated.
3. **Zone-Level Danger & Bottleneck Detection**:
   - Isolates individual high-risk choke points (e.g. *Darshan Queue* at $95\%$) even if total complex capacity appears acceptable.
4. **Automated Resource & Operational Allocation**:
   - Dynamically calculates exact security marshals, paramedic teams, and gate expansions scaled to crowd risk tier and critical saturation levels.
5. **Incident Lifecycle Command Center**:
   - Real-time incident ticketing allowing operators to acknowledge, track, and resolve zone breaches with complete audit history.
6. **Decision Analytics & Cross-Shrine Intelligence**:
   - Rolling time-series analytics, risk tier distributions, and side-by-side shrine comparison matrices across Gujarat temples.
7. **Controlled Hackathon Demo Scenario Progression**:
   - 4 deterministic scenarios (*Normal Day $\rightarrow$ Busy Weekend $\rightarrow$ Festival Rush $\rightarrow$ Emergency Overcrowding*) allowing live, instant demonstrations of the entire pipeline.

---

### 📊 F. Hackathon Demonstration Results (Gujarat Shrines)

| Scenario | Target Temple | Risk Tier | Unified Score | Primary Directives |
| :--- | :--- | :---: | :---: | :--- |
| **1. Normal Day** | Somnath | **`LOW`** | **`22.4%`** | 2 Security Units, 1 Medical Unit, 0 Additional Gates. Normal queue ops. |
| **2. Busy Weekend** | Dwarka | **`MODERATE`** | **`65.9%`** | 4 Security Units, 1 Medical Unit, +1 Additional Gate. Prepare overflow queues. |
| **3. Festival Rush** | Ambaji | **`HIGH`** | **`84.4%`** | 8 Security Units, 2 Medical Units, +2 Additional Gates, Standby Emergency Alert. |
| **4. Emergency Overcrowding** | Pavagadh | **`CRITICAL`** | **`86.6%`** | **20 Security Units**, **4 Medical Units**, **+3 Additional Gates**, Emergency Dispatch. |

#### Key Emergency Overcrowding Metrics (Pavagadh Hilltop Peak):
- **4 Critical Zones**: `Main Gate (92.0%)`, `Darshan Queue (95.0%)`, `Temple Entrance (94.0%)`, `Parking (90.0%)`
- **Security Allocation**: `20 units` (15 Base + 2 Surge + 3 Zone Intervention)
- **Medical Allocation**: `4 units`
- **Gate Openings**: `+3 emergency bypass gates`
- **Parking Directive**: `90.0% Saturation` $\rightarrow$ *"Redirect incoming vehicles to alternate parking."*
- **Emergency Priority**: **`CRITICAL`** (Active Emergency Dispatch Triggered)
