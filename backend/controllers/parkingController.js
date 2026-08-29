const Parking = require("../models/Parking");

// Get parking information for a temple
const getParkingByTemple = async (req, res) => {
  try {
    const parkingData = await Parking.find({
      temple: req.params.temple
    }).sort({ parkingName: 1 });

    const result = parkingData.map((parking) => {
      const availableSlots =
        parking.totalSlots - parking.occupiedSlots;

      const occupancyPercentage =
        parking.totalSlots === 0
          ? 0
          : Math.round(
              (parking.occupiedSlots / parking.totalSlots) * 100
            );

      let status = parking.status;

      if (parking.status !== "CLOSED") {
        if (availableSlots <= 0) {
          status = "FULL";
        } else {
          status = "OPEN";
        }
      }

      return {
        ...parking.toObject(),
        availableSlots,
        occupancyPercentage,
        status
      };
    });

    res.status(200).json({
      success: true,
      count: result.length,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch parking data",
      error: error.message
    });
  }
};

// Add parking area
const addParking = async (req, res) => {
  try {
    const {
      temple,
      parkingName,
      totalSlots,
      occupiedSlots,
      status
    } = req.body;

    if (
      !temple ||
      !parkingName ||
      totalSlots === undefined
    ) {
      return res.status(400).json({
        success: false,
        message:
          "Temple, parking name and total slots are required"
      });
    }

    if (
      occupiedSlots !== undefined &&
      occupiedSlots > totalSlots
    ) {
      return res.status(400).json({
        success: false,
        message: "Occupied slots cannot exceed total slots"
      });
    }

    const parking = await Parking.create({
      temple,
      parkingName,
      totalSlots,
      occupiedSlots: occupiedSlots || 0,
      status: status || "OPEN"
    });

    res.status(201).json({
      success: true,
      message: "Parking data added successfully",
      data: parking
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to add parking data",
      error: error.message
    });
  }
};

// Update parking occupancy
const updateParking = async (req, res) => {
  try {
    const parking = await Parking.findById(req.params.id);

    if (!parking) {
      return res.status(404).json({
        success: false,
        message: "Parking area not found"
      });
    }

    const {
      occupiedSlots,
      status
    } = req.body;

    if (
      occupiedSlots !== undefined &&
      occupiedSlots > parking.totalSlots
    ) {
      return res.status(400).json({
        success: false,
        message: "Occupied slots cannot exceed total slots"
      });
    }

    if (occupiedSlots !== undefined) {
      parking.occupiedSlots = occupiedSlots;
    }

    if (status !== undefined) {
      parking.status = status;
    }

    await parking.save();

    res.status(200).json({
      success: true,
      message: "Parking updated successfully",
      data: parking
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to update parking",
      error: error.message
    });
  }
};

module.exports = {
  getParkingByTemple,
  addParking,
  updateParking
};