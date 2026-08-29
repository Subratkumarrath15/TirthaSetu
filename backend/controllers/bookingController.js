const Booking = require("../models/Booking");
const QRCode = require("qrcode");

// Generate queue number
const generateQueueNumber = () => {
  const randomNumber = Math.floor(1000 + Math.random() * 9000);

  return `TS-${randomNumber}`;
};

// Create booking
const createBooking = async (req, res) => {
  try {
    const {
      pilgrimName,
      temple,
      visitDate,
      timeSlot,
      familySize,
      elderlyOrDisabled
    } = req.body;

    if (
      !pilgrimName ||
      !temple ||
      !visitDate ||
      !timeSlot ||
      !familySize
    ) {
      return res.status(400).json({
        success: false,
        message:
          "Pilgrim name, temple, visit date, time slot and family size are required"
      });
    }

    const queueNumber = generateQueueNumber();

    const booking = await Booking.create({
      pilgrimName,
      temple,
      visitDate,
      timeSlot,
      familySize,
      elderlyOrDisabled: elderlyOrDisabled || false,
      queueNumber
    });

    const qrPayload = JSON.stringify({
      bookingId: booking._id.toString(),
      queueNumber: booking.queueNumber,
      pilgrimName: booking.pilgrimName,
      temple: booking.temple,
      visitDate: booking.visitDate,
      timeSlot: booking.timeSlot,
      familySize: booking.familySize
    });

    const qrData = await QRCode.toDataURL(qrPayload);

    booking.qrData = qrData;

    await booking.save();

    res.status(201).json({
      success: true,
      message: "Smart Darshan booking confirmed",
      data: booking
    });
  } catch (error) {
    console.error("Booking error:", error);

    res.status(500).json({
      success: false,
      message: "Booking failed",
      error: error.message
    });
  }
};

// Get booking by ID
const getBookingById = async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id);

    if (!booking) {
      return res.status(404).json({
        success: false,
        message: "Booking not found"
      });
    }

    res.status(200).json({
      success: true,
      data: booking
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch booking",
      error: error.message
    });
  }
};

// Get all bookings for a temple
const getBookingsByTemple = async (req, res) => {
  try {
    const bookings = await Booking.find({
      temple: req.params.temple
    }).sort({
      createdAt: -1
    });

    res.status(200).json({
      success: true,
      count: bookings.length,
      data: bookings
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch bookings",
      error: error.message
    });
  }
};

module.exports = {
  createBooking,
  getBookingById,
  getBookingsByTemple
};