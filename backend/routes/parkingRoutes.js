const express = require("express");

const {
  getParkingByTemple,
  addParking,
  updateParking
} = require("../controllers/parkingController");

const router = express.Router();

// Get parking for a temple
router.get("/:temple", getParkingByTemple);

// Add parking area
router.post("/", addParking);

// Update parking
router.patch("/:id", updateParking);

module.exports = router;