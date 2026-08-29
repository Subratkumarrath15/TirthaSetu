const mongoose = require("mongoose");

const templeSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      unique: true,
      trim: true
    },

    location: {
      type: String,
      required: true
    },

    state: {
      type: String,
      default: "Gujarat"
    },

    openingTime: {
      type: String
    },

    closingTime: {
      type: String
    },

    description: {
      type: String
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Temple", templeSchema);