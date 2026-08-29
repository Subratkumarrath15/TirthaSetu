const mongoose = require("mongoose");

const notificationSchema = new mongoose.Schema(
  {
    temple: {
      type: String,
      required: true,
      trim: true
    },

    type: {
      type: String,
      enum: [
        "CROWD",
        "TRAFFIC",
        "EMERGENCY",
        "DARSHAN",
        "PARKING",
        "SYSTEM"
      ],
      required: true
    },

    title: {
      type: String,
      required: true,
      trim: true
    },

    message: {
      type: String,
      required: true,
      trim: true
    },

    severity: {
      type: String,
      enum: ["INFO", "WARNING", "CRITICAL"],
      default: "INFO"
    },

    target: {
      type: String,
      enum: ["PILGRIM", "ADMIN", "BOTH"],
      default: "BOTH"
    },

    isRead: {
      type: Boolean,
      default: false
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model(
  "Notification",
  notificationSchema
);