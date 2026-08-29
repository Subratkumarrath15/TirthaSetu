const express = require("express");

const {
  createNotification,
  getNotificationsByTemple,
  getUnreadNotifications,
  markNotificationAsRead
} = require("../controllers/notificationController");

const router = express.Router();

// Create notification
router.post("/", createNotification);

// Get all notifications for temple
router.get("/temple/:temple", getNotificationsByTemple);

// Get unread notifications
router.get("/unread/:temple", getUnreadNotifications);

// Mark notification as read
router.patch("/:id/read", markNotificationAsRead);

module.exports = router;