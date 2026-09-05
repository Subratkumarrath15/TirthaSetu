const { requestML } = require("../services/mlService");

const getPrediction = async (req, res) => {
  try {
    const temple = req.params.temple;

    const result = await requestML(`/api/predict/${encodeURIComponent(temple)}`, {
      query: {
        hour: req.query.hour ?? 13,
        day_of_week: req.query.day_of_week ?? "Sunday",
        is_weekend: req.query.is_weekend ?? 1,
        is_holiday: req.query.is_holiday ?? 0,
        is_festival: req.query.is_festival ?? 0,
        weather: req.query.weather ?? "Clear",
        temperature: req.query.temperature ?? 32,
        previous_visitors: req.query.previous_visitors ?? 0,
        current_crowd: req.query.current_crowd ?? 0
      }
    });
    res.status(result.status).json(result.data);

  } catch (error) {
    console.error("Prediction service error:", error.message);

    res.status(503).json({
      success: false,
      message: "Could not connect to AI prediction service",
      detail: error.message
    });
  }
};

module.exports = {
  getPrediction
};
