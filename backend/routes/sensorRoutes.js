const express = require("express");

const {
  addSensorData,
  getSensorDataByTemple,
  getLatestSensorReading
} = require("../controllers/sensorController");

const router = express.Router();

// Receive sensor data
router.post("/", addSensorData);

// Get sensor data for a temple
router.get("/temple/:temple", getSensorDataByTemple);

// Get latest reading of one sensor
router.get("/:sensorId", getLatestSensorReading);

module.exports = router;