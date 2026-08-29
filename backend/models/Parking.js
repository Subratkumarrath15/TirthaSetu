const mongoose = require("mongoose");

const parkingSchema = new mongoose.Schema(
  {
    temple: {
      type: String,
      required: true,
      trim: true
    },

    parkingName: {
      type: String,
      required: true,
      trim: true
    },

    totalSlots: {
      type: Number,
      required: true,
      min: 0
    },

    occupiedSlots: {
      type: Number,
      default: 0,
      min: 0
    },

    status: {
      type: String,
      enum: ["OPEN", "FULL", "CLOSED"],
      default: "OPEN"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Parking", parkingSchema);