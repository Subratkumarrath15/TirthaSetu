const mongoose = require("mongoose");

const bookingSchema = new mongoose.Schema(
  {
    pilgrimName: {
      type: String,
      required: true,
      trim: true
    },

    temple: {
      type: String,
      required: true,
      trim: true
    },

    visitDate: {
      type: String,
      required: true
    },

    timeSlot: {
      type: String,
      required: true
    },

    familySize: {
      type: Number,
      required: true,
      min: 1,
      max: 20
    },

    elderlyOrDisabled: {
      type: Boolean,
      default: false
    },

    queueNumber: {
      type: String,
      unique: true,
      required: true
    },

    qrData: {
      type: String,
      default: ""
    },

    status: {
      type: String,
      enum: ["CONFIRMED", "CANCELLED", "COMPLETED"],
      default: "CONFIRMED"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Booking", bookingSchema);