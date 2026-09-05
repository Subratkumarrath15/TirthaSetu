const express = require("express");
const { requestML } = require("../services/mlService");

const router = express.Router();
const SUPPORTED_TEMPLES = new Set(["Somnath", "Dwarka", "Ambaji", "Pavagadh"]);

const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function buildContext(query = {}) {
  const now = new Date();
  return {
    hour: query.hour ?? now.getHours(),
    day_of_week: query.day_of_week ?? dayNames[now.getDay()],
    is_weekend: query.is_weekend ?? ([0, 6].includes(now.getDay()) ? 1 : 0),
    is_holiday: query.is_holiday ?? 0,
    is_festival: query.is_festival ?? 0,
    weather: query.weather ?? "Clear",
    temperature: query.temperature ?? 30,
    previous_visitors: query.previous_visitors ?? 0
  };
}

async function proxyML(res, path, options) {
  try {
    const result = await requestML(path, options);
    return res.status(result.status).json(result.data);
  } catch (error) {
    return res.status(503).json({
      success: false,
      message: "ML service is unavailable. Start the FastAPI service on port 8000.",
      detail: error.name === "AbortError" ? "ML service request timed out." : error.message
    });
  }
}

function validateTemple(req, res, next) {
  if (!SUPPORTED_TEMPLES.has(req.params.temple)) {
    return res.status(404).json({
      success: false,
      message: `Unsupported temple. Supported temples are: ${[...SUPPORTED_TEMPLES].join(", ")}`
    });
  }
  next();
}

router.get("/temples", (req, res) => proxyML(res, "/api/temples"));

router.get("/full-status/:temple", validateTemple, (req, res) =>
  proxyML(res, `/api/full-status/${encodeURIComponent(req.params.temple)}`, { query: buildContext(req.query) })
);

router.get("/realtime/:temple", validateTemple, (req, res) =>
  proxyML(res, `/api/realtime/${encodeURIComponent(req.params.temple)}`)
);

router.get("/predict/:temple", validateTemple, (req, res) =>
  proxyML(res, `/api/predict/${encodeURIComponent(req.params.temple)}`, {
    query: { ...buildContext(req.query), current_crowd: req.query.current_crowd ?? 0 }
  })
);
router.get("/intelligence/:temple", validateTemple, (req, res) =>
  proxyML(res, `/api/intelligence/${encodeURIComponent(req.params.temple)}`, { query: buildContext(req.query) })
);
router.get("/recommendations/:temple", validateTemple, (req, res) =>
  proxyML(res, `/api/recommendations/${encodeURIComponent(req.params.temple)}`, { query: buildContext(req.query) })
);
router.get("/incidents/active", (req, res) => proxyML(res, "/api/incidents/active", { query: req.query }));
router.get("/incidents/history", (req, res) => proxyML(res, "/api/incidents/history", { query: req.query }));
router.post("/incidents/:id/acknowledge", (req, res) =>
  proxyML(res, `/api/incidents/${encodeURIComponent(req.params.id)}/acknowledge`, { method: "POST" })
);
router.post("/incidents/:id/resolve", (req, res) =>
  proxyML(res, `/api/incidents/${encodeURIComponent(req.params.id)}/resolve`, { method: "POST" })
);
router.get("/analytics/summary", (req, res) => proxyML(res, "/api/analytics/summary"));
router.get("/analytics/trends", (req, res) => proxyML(res, "/api/analytics/trends", { query: req.query }));
router.get("/analytics/risk-distribution", (req, res) => proxyML(res, "/api/analytics/risk-distribution"));
router.get("/analytics/temple-comparison", (req, res) => proxyML(res, "/api/analytics/temple-comparison"));
router.get("/analytics/incidents", (req, res) => proxyML(res, "/api/analytics/incidents"));

module.exports = router;
