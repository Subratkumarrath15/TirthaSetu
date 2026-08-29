const Resource = require("../models/Resource");

const calculateResources = (riskLevel) => {
  if (riskLevel === "LOW") {
    return {
      securityPersonnel: 10,
      medicalStaff: 2,
      volunteers: 10,
      ambulances: 1
    };
  }

  if (riskLevel === "MEDIUM") {
    return {
      securityPersonnel: 18,
      medicalStaff: 4,
      volunteers: 20,
      ambulances: 1
    };
  }

  if (riskLevel === "HIGH") {
    return {
      securityPersonnel: 30,
      medicalStaff: 7,
      volunteers: 36,
      ambulances: 2
    };
  }

  if (riskLevel === "CRITICAL") {
    return {
      securityPersonnel: 45,
      medicalStaff: 10,
      volunteers: 50,
      ambulances: 3
    };
  }

  return null;
};


const getResourceRecommendation = async (req, res) => {
  try {
    const temple = req.params.temple;
    const riskLevel = req.query.riskLevel;

    if (!riskLevel) {
      return res.status(400).json({
        success: false,
        message: "riskLevel is required"
      });
    }

    const allowedRiskLevels = [
      "LOW",
      "MEDIUM",
      "HIGH",
      "CRITICAL"
    ];

    if (!allowedRiskLevels.includes(riskLevel)) {
      return res.status(400).json({
        success: false,
        message:
          "riskLevel must be LOW, MEDIUM, HIGH or CRITICAL"
      });
    }

    const resources = calculateResources(riskLevel);

    res.status(200).json({
      success: true,
      data: {
        temple: temple,
        crowdRisk: riskLevel,
        recommendedResources: resources
      }
    });

  } catch (error) {
    console.error(error);

    res.status(500).json({
      success: false,
      message: "Failed to calculate resources",
      error: error.message
    });
  }
};


const createResourcePlan = async (req, res) => {
  try {
    const {
      temple,
      securityPersonnel,
      medicalStaff,
      volunteers,
      ambulances,
      crowdRisk
    } = req.body;

    if (!temple || !crowdRisk) {
      return res.status(400).json({
        success: false,
        message: "Temple and crowdRisk are required"
      });
    }

    const resourcePlan = await Resource.create({
      temple,
      securityPersonnel: securityPersonnel || 0,
      medicalStaff: medicalStaff || 0,
      volunteers: volunteers || 0,
      ambulances: ambulances || 0,
      crowdRisk,
      status: "RECOMMENDED"
    });

    res.status(201).json({
      success: true,
      message: "Resource plan created successfully",
      data: resourcePlan
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to create resource plan",
      error: error.message
    });
  }
};


const getResourcePlans = async (req, res) => {
  try {
    const plans = await Resource.find({
      temple: req.params.temple
    }).sort({ createdAt: -1 });

    res.status(200).json({
      success: true,
      count: plans.length,
      data: plans
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch resource plans",
      error: error.message
    });
  }
};


const updateResourceStatus = async (req, res) => {
  try {
    const { status } = req.body;

    const resourcePlan =
      await Resource.findByIdAndUpdate(
        req.params.id,
        { status },
        { new: true }
      );

    if (!resourcePlan) {
      return res.status(404).json({
        success: false,
        message: "Resource plan not found"
      });
    }

    res.status(200).json({
      success: true,
      message: "Resource status updated",
      data: resourcePlan
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to update resource",
      error: error.message
    });
  }
};


module.exports = {
  getResourceRecommendation,
  createResourcePlan,
  getResourcePlans,
  updateResourceStatus
};