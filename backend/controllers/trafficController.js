const Traffic = require("../models/Traffic");

const getTrafficByTemple = async (req, res) => {
  try {
    const traffic = await Traffic.find({
      temple: req.params.temple
    }).sort({ roadName: 1 });

    res.status(200).json({
      success: true,
      count: traffic.length,
      data: traffic
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch traffic data",
      error: error.message
    });
  }
};


const addTraffic = async (req, res) => {
  try {
    const {
      temple,
      roadName,
      trafficLevel,
      vehicleCount,
      averageSpeed,
      recommended,
      shuttleAvailable
    } = req.body;

    if (!temple || !roadName) {
      return res.status(400).json({
        success: false,
        message: "Temple and roadName are required"
      });
    }

    const traffic = await Traffic.create({
      temple,
      roadName,
      trafficLevel: trafficLevel || "LOW",
      vehicleCount: vehicleCount || 0,
      averageSpeed: averageSpeed || 0,
      recommended: recommended || false,
      shuttleAvailable: shuttleAvailable || false
    });

    res.status(201).json({
      success: true,
      message: "Traffic data added successfully",
      data: traffic
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to add traffic data",
      error: error.message
    });
  }
};


const updateTraffic = async (req, res) => {
  try {
    const traffic = await Traffic.findByIdAndUpdate(
      req.params.id,
      req.body,
      {
        new: true,
        runValidators: true
      }
    );

    if (!traffic) {
      return res.status(404).json({
        success: false,
        message: "Traffic record not found"
      });
    }

    res.status(200).json({
      success: true,
      message: "Traffic data updated successfully",
      data: traffic
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to update traffic data",
      error: error.message
    });
  }
};


module.exports = {
  getTrafficByTemple,
  addTraffic,
  updateTraffic
};