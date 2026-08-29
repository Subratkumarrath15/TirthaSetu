const mongoose = require("mongoose");

const trafficSchema = new mongoose.Schema(
  {
    temple: {
      type: String,
      required: true,
      trim: true
    },

    roadName: {
      type: String,
      required: true,
      trim: true
    },

    trafficLevel: {
      type: String,
      enum: ["LOW", "MEDIUM", "HIGH", "CLOSED"],
      default: "LOW"
    },

    vehicleCount: {
      type: Number,
      default: 0,
      min: 0
    },

    averageSpeed: {
      type: Number,
      default: 0,
      min: 0
    },

    recommended: {
      type: Boolean,
      default: false
    },

    shuttleAvailable: {
      type: Boolean,
      default: false
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Traffic", trafficSchema);