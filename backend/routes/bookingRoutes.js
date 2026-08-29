const express = require("express");

const {
  createBooking,
  getBookingById,
  getBookingsByTemple
} = require("../controllers/bookingController");

const router = express.Router();

// Create a booking
router.post("/", createBooking);

// Get booking by ID
router.get("/:id", getBookingById);

// Get all bookings for a temple
router.get("/temple/:temple", getBookingsByTemple);

module.exports = router;