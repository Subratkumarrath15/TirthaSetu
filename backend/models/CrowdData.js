const mongoose = require("mongoose");

const crowdDataSchema = new mongoose.Schema(
  {
    temple: {
      type: String,
      required: true,
      trim: true
    },

    zone: {
      type: String,
      required: true,
      trim: true
    },

    density: {
      type: Number,
      required: true,
      min: 0,
      max: 100
    },

    visitorsPerMinute: {
      type: Number,
      default: 0
    },

    waitTime: {
      type: Number,
      default: 0
    },

    riskLevel: {
      type: String,
      enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
      default: "LOW"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("CrowdData", crowdDataSchema);