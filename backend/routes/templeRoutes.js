const express = require("express");

const {
  getAllTemples,
  getTempleByName
} = require("../controllers/templeController");

const router = express.Router();

// GET all temples
router.get("/", getAllTemples);

// GET one temple by name
router.get("/:name", getTempleByName);

module.exports = router;