/**
 * TirthaSetu Node.js / Express Crowd Controller & Route Integration
 *
 * Intermediary proxy and aggregator service connecting the Node.js Express backend
 * to the Python FastAPI AI + Real-Time Microservice (http://127.0.0.1:8000).
 */

const axios = require('axios');
const express = require('express');
const router = express.Router();

const AI_MICROSERVICE_URL = process.env.AI_MICROSERVICE_URL || 'http://127.0.0.1:8000';

/**
 * Helper to compute default temporal context for requests
 */
function getDefaultContext(query = {}) {
  const now = new Date();
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  return {
    hour: query.hour !== undefined ? query.hour : now.getHours(),
    day_of_week: query.day_of_week || dayNames[now.getDay()],
    is_weekend: query.is_weekend !== undefined ? query.is_weekend : ((now.getDay() === 0 || now.getDay() === 6) ? 1 : 0),
    is_holiday: query.is_holiday !== undefined ? query.is_holiday : 0,
    is_festival: query.is_festival !== undefined ? query.is_festival : 0,
    weather: query.weather || 'Sunny',
    temperature: query.temperature !== undefined ? query.temperature : 30.0,
    previous_visitors: query.previous_visitors !== undefined ? query.previous_visitors : 4500,
  };
}

/**
 * GET /api/dashboard/temples
 * Retrieve supported temple catalog
 */
router.get('/temples', async (req, res) => {
  try {
    const response = await axios.get(`${AI_MICROSERVICE_URL}/api/temples`);
    return res.status(200).json(response.data);
  } catch (err) {
    console.error('[TirthaSetu AI Error] Failed to fetch temples:', err.message);
    return res.status(err.response?.status || 500).json({
      error: 'Failed to fetch temple list',
      details: err.message,
    });
  }
});

/**
 * GET /api/dashboard/full-status/:temple
 * Unified master endpoint for government dashboard cards
 */
router.get('/full-status/:temple', async (req, res) => {
  const { temple } = req.params;
  const params = getDefaultContext(req.query);

  try {
    const response = await axios.get(`${AI_MICROSERVICE_URL}/api/full-status/${encodeURIComponent(temple)}`, { params });
    return res.status(200).json(response.data);
  } catch (err) {
    console.error(`[TirthaSetu AI Error] Failed to fetch full status for ${temple}:`, err.message);
    return res.status(err.response?.status || 500).json({
      error: `Failed to fetch status for ${temple}`,
      details: err.response?.data || err.message,
    });
  }
});

/**
 * GET /api/dashboard/demo/:scenario
 * Trigger controlled hackathon demo scenario
 */
router.get('/demo/:scenario', async (req, res) => {
  const { scenario } = req.params;

  try {
    const response = await axios.get(`${AI_MICROSERVICE_URL}/api/demo/${encodeURIComponent(scenario)}`);
    return res.status(200).json(response.data);
  } catch (err) {
    console.error(`[TirthaSetu AI Error] Demo scenario ${scenario} failed:`, err.message);
    return res.status(err.response?.status || 500).json({
      error: `Failed to execute demo scenario ${scenario}`,
      details: err.response?.data || err.message,
    });
  }
});

module.exports = router;
