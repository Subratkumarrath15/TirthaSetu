const CrowdData = require("../models/CrowdData");

// Calculate crowd risk
const calculateRisk = (density) => {
  if (density >= 90) {
    return "CRITICAL";
  }

  if (density >= 75) {
    return "HIGH";
  }

  if (density >= 50) {
    return "MEDIUM";
  }

  return "LOW";
};

// Add crowd data
const addCrowdData = async (req, res) => {
  try {
    const {
      temple,
      zone,
      density,
      visitorsPerMinute,
      waitTime
    } = req.body;

    if (!temple || !zone || density === undefined) {
      return res.status(400).json({
        success: false,
        message: "Temple, zone and density are required"
      });
    }

    const riskLevel = calculateRisk(density);

    const crowdData = await CrowdData.create({
      temple,
      zone,
      density,
      visitorsPerMinute,
      waitTime,
      riskLevel
    });

    res.status(201).json({
      success: true,
      message: "Crowd data added successfully",
      data: crowdData
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to add crowd data",
      error: error.message
    });
  }
};

// Get crowd data for a temple
const getCrowdData = async (req, res) => {
  try {
    const crowdData = await CrowdData.find({
      temple: req.params.temple
    }).sort({
      createdAt: -1
    });

    res.status(200).json({
      success: true,
      count: crowdData.length,
      data: crowdData
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch crowd data",
      error: error.message
    });
  }
};

module.exports = {
  addCrowdData,
  getCrowdData
};