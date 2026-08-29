const SensorData = require("../models/SensorData");

// Add sensor data
const addSensorData = async (req, res) => {
  try {
    const {
      temple,
      sensorId,
      sensorType,
      zone,
      value,
      unit,
      status
    } = req.body;

    // Validate required fields
    if (
      !temple ||
      !sensorId ||
      !sensorType ||
      value === undefined
    ) {
      return res.status(400).json({
        success: false,
        message:
          "Temple, sensorId, sensorType and value are required"
      });
    }

    // Basic validation for numeric values
    if (typeof value !== "number") {
      return res.status(400).json({
        success: false,
        message: "Sensor value must be a number"
      });
    }

    const sensor = await SensorData.create({
      temple,
      sensorId,
      sensorType,
      zone: zone || "",
      value,
      unit: unit || "",
      status: status || "ONLINE"
    });

    res.status(201).json({
      success: true,
      message: "Sensor data stored successfully",
      data: sensor
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to store sensor data",
      error: error.message
    });
  }
};

// Get all sensor data for one temple
const getSensorDataByTemple = async (req, res) => {
  try {
    const sensors = await SensorData.find({
      temple: req.params.temple
    }).sort({
      createdAt: -1
    });

    res.status(200).json({
      success: true,
      count: sensors.length,
      data: sensors
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch sensor data",
      error: error.message
    });
  }
};

// Get latest reading for one sensor
const getLatestSensorReading = async (req, res) => {
  try {
    const sensor = await SensorData.findOne({
      sensorId: req.params.sensorId
    }).sort({
      createdAt: -1
    });

    if (!sensor) {
      return res.status(404).json({
        success: false,
        message: "Sensor not found"
      });
    }

    res.status(200).json({
      success: true,
      data: sensor
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch sensor reading",
      error: error.message
    });
  }
};

module.exports = {
  addSensorData,
  getSensorDataByTemple,
  getLatestSensorReading
};