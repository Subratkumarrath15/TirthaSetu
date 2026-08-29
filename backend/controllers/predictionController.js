const getPrediction = async (req, res) => {
  try {
    const temple = req.params.temple;

    const response = await fetch(
      "http://127.0.0.1:8000/predict",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          temple: temple,
          day_of_week: "Sunday",
          is_weekend: 1,
          is_holiday: 0,
          is_festival: 0,
          hour: 13,
          temperature: 32,
          previous_visitors: 24000
        })
      }
    );

    const result = await response.json();

    if (!response.ok) {
      return res.status(500).json({
        success: false,
        message: "AI prediction service returned an error",
        data: result
      });
    }

    res.status(200).json(result);

  } catch (error) {
    console.error("Prediction service error:", error.message);

    res.status(500).json({
      success: false,
      message: "Could not connect to AI prediction service",
      error: error.message
    });
  }
};

module.exports = {
  getPrediction
};