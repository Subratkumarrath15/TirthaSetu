const express = require("express");

const {
  addCrowdData,
  getCrowdData
} = require("../controllers/crowdController");

const router = express.Router();

router.post("/", addCrowdData);

router.get("/:temple", getCrowdData);

module.exports = router;