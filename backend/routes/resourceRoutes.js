const express = require("express");

const {
  getResourceRecommendation,
  createResourcePlan,
  getResourcePlans,
  updateResourceStatus
} = require("../controllers/resourceController");

const router = express.Router();

router.get(
  "/recommendation/:temple",
  getResourceRecommendation
);

router.post(
  "/",
  createResourcePlan
);

router.get(
  "/temple/:temple",
  getResourcePlans
);

router.patch(
  "/:id",
  updateResourceStatus
);

module.exports = router;