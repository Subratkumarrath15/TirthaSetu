const Emergency = require("../models/Emergency");

// Create emergency alert
const createEmergency = async (req, res) => {
  try {
    const {
      temple,
      type,
      description,
      zone
    } = req.body;

    if (!temple || !type) {
      return res.status(400).json({
        success: false,
        message: "Temple and emergency type are required"
      });
    }

    const emergency = await Emergency.create({
      temple,
      type,
      description: description || "",
      zone: zone || "Unknown"
    });

    res.status(201).json({
      success: true,
      message: "Emergency alert created successfully",
      data: emergency
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to create emergency alert",
      error: error.message
    });
  }
};

// Get all emergency alerts
const getAllEmergencies = async (req, res) => {
  try {
    const emergencies = await Emergency.find()
      .sort({ createdAt: -1 });

    res.status(200).json({
      success: true,
      count: emergencies.length,
      data: emergencies
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch emergency alerts",
      error: error.message
    });
  }
};

// Get emergencies for one temple
const getEmergenciesByTemple = async (req, res) => {
  try {
    const emergencies = await Emergency.find({
      temple: req.params.temple
    }).sort({ createdAt: -1 });

    res.status(200).json({
      success: true,
      count: emergencies.length,
      data: emergencies
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch temple emergencies",
      error: error.message
    });
  }
};

// Update emergency status
const updateEmergencyStatus = async (req, res) => {
  try {
    const { status } = req.body;

    const allowedStatuses = [
      "PENDING",
      "ASSIGNED",
      "RESOLVED"
    ];

    if (!allowedStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        message:
          "Status must be PENDING, ASSIGNED, or RESOLVED"
      });
    }

    const emergency =
      await Emergency.findByIdAndUpdate(
        req.params.id,
        { status },
        { new: true }
      );

    if (!emergency) {
      return res.status(404).json({
        success: false,
        message: "Emergency alert not found"
      });
    }

    res.status(200).json({
      success: true,
      message: "Emergency status updated successfully",
      data: emergency
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to update emergency status",
      error: error.message
    });
  }
};

module.exports = {
  createEmergency,
  getAllEmergencies,
  getEmergenciesByTemple,
  updateEmergencyStatus
};