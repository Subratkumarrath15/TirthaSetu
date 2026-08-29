const mongoose = require("mongoose");

const emergencySchema = new mongoose.Schema(
  {
    temple: {
      type: String,
      required: true,
      trim: true
    },

    type: {
      type: String,
      enum: [
        "MEDICAL",
        "SAFETY",
        "LOST_PERSON",
        "CROWD_PANIC"
      ],
      required: true
    },

    description: {
      type: String,
      default: "",
      trim: true
    },

    zone: {
      type: String,
      default: "Unknown",
      trim: true
    },

    status: {
      type: String,
      enum: [
        "PENDING",
        "ASSIGNED",
        "RESOLVED"
      ],
      default: "PENDING"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Emergency", emergencySchema);