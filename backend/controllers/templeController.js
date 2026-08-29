const Temple = require("../models/Temple");

// Get all temples
const getAllTemples = async (req, res) => {
  try {
    const temples = await Temple.find().sort({ name: 1 });

    res.status(200).json({
      success: true,
      count: temples.length,
      data: temples
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch temples",
      error: error.message
    });
  }
};

// Get one temple
const getTempleByName = async (req, res) => {
  try {
    const temple = await Temple.findOne({
      name: req.params.name
    });

    if (!temple) {
      return res.status(404).json({
        success: false,
        message: "Temple not found"
      });
    }

    res.status(200).json({
      success: true,
      data: temple
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch temple",
      error: error.message
    });
  }
};

module.exports = {
  getAllTemples,
  getTempleByName
};