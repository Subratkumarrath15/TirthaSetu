# TirthaSetu Frontend

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

## Integration

The React application calls only the Node gateway at `http://localhost:5000`.
Node proxies live ML status at `GET /api/ai/full-status/:temple`; bookings and
emergency requests continue through `POST /api/bookings` and `POST /api/emergency`.
Set `VITE_API_BASE` only when the gateway is hosted elsewhere.
