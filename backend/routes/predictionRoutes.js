const express = require("express");

const {
  getPrediction
} = require("../controllers/predictionController");

const router = express.Router();

router.get("/:temple", getPrediction);

module.exports = router;
