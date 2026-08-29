const express = require("express");

const {
  createEmergency,
  getAllEmergencies,
  getEmergenciesByTemple,
  updateEmergencyStatus
} = require("../controllers/emergencyController");

const router = express.Router();

// Create emergency alert
router.post("/", createEmergency);

// Get all emergencies
router.get("/", getAllEmergencies);

// Get emergencies for a temple
router.get("/temple/:temple", getEmergenciesByTemple);

// Update emergency status
router.patch("/:id", updateEmergencyStatus);

module.exports = router;
