const express = require("express");

const {
  getTrafficByTemple,
  addTraffic,
  updateTraffic
} = require("../controllers/trafficController");

const router = express.Router();

router.get("/:temple", getTrafficByTemple);

router.post("/", addTraffic);

router.patch("/:id", updateTraffic);

module.exports = router;