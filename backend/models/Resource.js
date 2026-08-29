const mongoose = require("mongoose");

const resourceSchema = new mongoose.Schema(
  {
    temple: {
      type: String,
      required: true,
      trim: true
    },

    securityPersonnel: {
      type: Number,
      default: 0,
      min: 0
    },

    medicalStaff: {
      type: Number,
      default: 0,
      min: 0
    },

    volunteers: {
      type: Number,
      default: 0,
      min: 0
    },

    ambulances: {
      type: Number,
      default: 0,
      min: 0
    },

    crowdRisk: {
      type: String,
      enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
      default: "LOW"
    },

    status: {
      type: String,
      enum: ["NORMAL", "RECOMMENDED", "DEPLOYED"],
      default: "NORMAL"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Resource", resourceSchema);