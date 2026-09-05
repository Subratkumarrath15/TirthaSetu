# TirthaSetu: Final Hackathon Presentation & Demo Checklist (Gujarat Shrines)

---

## 🛠️ 1. Pre-Demo Preparation Checklist

- [ ] **Laptop Battery**: Fully charged and power adapter connected.
- [ ] **Offline Readiness**: Ensure system runs completely locally on `127.0.0.1:8000` (no internet connectivity required).
- [ ] **Virtual Environment**: Verified activated (`.\.venv\Scripts\activate`).
- [ ] **Background Services Active**:
  - [ ] IoT Sensor Simulator running in terminal: `python realtime/sensor_simulator.py`
  - [ ] FastAPI Backend running on port 8000: `python -m uvicorn api.prediction_api:app --host 127.0.0.1 --port 8000`
- [ ] **Model Artifact Check**: Verified `models/crowd_model.pkl` loads without error.
- [ ] **Dashboard Check**: Opened `http://127.0.0.1:8000/dashboard` in Google Chrome / Edge.
- [ ] **Swagger Documentation**: Verified accessible at `http://127.0.0.1:8000/docs`.
- [ ] **Scenario Testing (4 Gujarat Shrines)**:
  - [ ] Clicked `1. Normal Day (LOW)` $\rightarrow$ Verified green UI (**Somnath** ~22.4%)
  - [ ] Clicked `2. Busy Weekend (MODERATE)` $\rightarrow$ Verified yellow UI (**Dwarka** ~65.9%)
  - [ ] Clicked `3. Festival Rush (HIGH)` $\rightarrow$ Verified orange UI (**Ambaji** ~84.4%)
  - [ ] Clicked `4. Emergency Overcrowding (CRITICAL)` $\rightarrow$ Verified red UI (**Pavagadh** ~86.6%, 4 critical alerts, 20 security units)
  - [ ] Clicked `Live Sensor Feed` $\rightarrow$ Verified returning to dynamic simulator feed.
- [ ] **Display Setup**:
  - [ ] Browser zoom set to 90% or 100% so all KPIs, charts, and directives fit cleanly on screen.
  - [ ] Clean desktop: closed unnecessary chat apps, IDE sidebars, and cluttered terminal windows.

---

## 🎤 2. During-Demo Execution Checklist

- [ ] **Opening (0:00 - 0:15)**: Start in **Live Sensor Feed** mode on **Somnath**. Clearly state the core problem of crowd surges at Gujarat pilgrimage sites.
- [ ] **Architecture (0:15 - 0:35)**: Highlight the 40/60 AI Forecast + Live IoT sensor fusion.
- [ ] **Progression (0:35 - 1:15)**:
  - [ ] Click `Normal Day` (Somnath) $\rightarrow$ Show low risk baseline.
  - [ ] Click `Busy Weekend` (Dwarka) $\rightarrow$ Show moderate scaling.
  - [ ] Click `Festival Rush` (Ambaji) $\rightarrow$ Show high risk warnings and automated gate expansions.
- [ ] **Climax Demo (1:15 - 1:45)**:
  - [ ] Click `Emergency Overcrowding` (**Pavagadh**).
  - [ ] Point out the **95.0%** Darshan Queue saturation.
  - [ ] Highlight the **20 Security Units** and **4 Medical Teams**.
  - [ ] Scroll to the **Active Incident Command Center** $\rightarrow$ Click **Acknowledge** on a critical ticket.
  - [ ] Click **Resolve** to show completed dispatch.
- [ ] **Executive Insights (1:45 - 2:00)**: Point to **Analytics & Decision Insights** charts and state the final punchline on saving lives.

---

## 💾 3. Emergency Backup Checklist

- [ ] **Offline Screenshots**: High-resolution screenshots of all 4 scenarios stored in `docs/screenshots/` or presentation slides.
- [ ] **Test Report Copy**: Output of `demo/test_end_to_end.py` saved in presentation notes.
- [ ] **Swagger JSON**: `http://127.0.0.1:8000/openapi.json` cached locally.
- [ ] **Single-Click Batch Launcher**: Verified `start_tirthasetu.bat` starts the entire stack with one double-click.
