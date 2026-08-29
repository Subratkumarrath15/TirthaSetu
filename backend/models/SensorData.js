const mongoose = require("mongoose");

const sensorDataSchema = new mongoose.Schema(
  {
    temple: {
      type: String,
      required: true,
      trim: true
    },

    sensorId: {
      type: String,
      required: true,
      trim: true
    },

    sensorType: {
      type: String,
      enum: [
        "PEOPLE_COUNTER",
        "DENSITY",
        "PARKING",
        "EMERGENCY"
      ],
      required: true
    },

    zone: {
      type: String,
      default: "",
      trim: true
    },

    value: {
      type: Number,
      required: true
    },

    unit: {
      type: String,
      default: ""
    },

    status: {
      type: String,
      enum: ["ONLINE", "OFFLINE", "WARNING"],
      default: "ONLINE"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model(
  "SensorData",
  sensorDataSchema
);