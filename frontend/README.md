# YatraSafe Frontend

React + Vite frontend prototype for the Gujarat pilgrimage crowd-management hackathon.

## Included
- Pilgrim portal for Somnath, Dwarka, Ambaji, Pavagadh
- Live/simulated crowd status and wait time
- AI-recommended visit window
- Smart darshan booking with demo QR pass
- Parking + route guidance
- Accessibility assistance workflow
- Multilingual selector (EN / Hindi / Gujarati)
- SOS: medical, safety, lost child, crowd panic
- Zone-level crowd heatmap
- Government control-room dashboard
- AI forecast visualization
- Resource allocation
- IoT sensor feed (software simulation)
- Emergency/incident center
- Parking and traffic intelligence
- Cross-temple operational overview

## Run
npm install
npm run dev

## Backend integration later
Replace mock values in `src/main.jsx` with API calls from Node/Express. Suggested APIs:
GET /api/temples
GET /api/crowd/:temple
GET /api/prediction/:temple
GET /api/parking/:temple
GET /api/sensors/:temple
POST /api/bookings
POST /api/emergency
POST /api/assistance

The UI intentionally works without a backend so the team can demo it immediately.
