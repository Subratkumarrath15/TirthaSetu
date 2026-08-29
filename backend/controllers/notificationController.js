const Notification = require("../models/Notification");

// ---------------------------------------------
// Create notification
// ---------------------------------------------

const createNotification = async (req, res) => {
  try {
    const {
      temple,
      type,
      title,
      message,
      severity,
      target
    } = req.body;

    if (!temple || !type || !title || !message) {
      return res.status(400).json({
        success: false,
        message:
          "Temple, type, title and message are required"
      });
    }

    const notification = await Notification.create({
      temple,
      type,
      title,
      message,
      severity: severity || "INFO",
      target: target || "BOTH"
    });

    res.status(201).json({
      success: true,
      message: "Notification created successfully",
      data: notification
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to create notification",
      error: error.message
    });
  }
};


// ---------------------------------------------
// Get notifications for a temple
// ---------------------------------------------

const getNotificationsByTemple = async (req, res) => {
  try {
    const notifications = await Notification.find({
      temple: req.params.temple
    }).sort({
      createdAt: -1
    });

    res.status(200).json({
      success: true,
      count: notifications.length,
      data: notifications
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch notifications",
      error: error.message
    });
  }
};


// ---------------------------------------------
// Get unread notifications
// ---------------------------------------------

const getUnreadNotifications = async (req, res) => {
  try {
    const notifications = await Notification.find({
      temple: req.params.temple,
      isRead: false
    }).sort({
      createdAt: -1
    });

    res.status(200).json({
      success: true,
      count: notifications.length,
      data: notifications
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch unread notifications",
      error: error.message
    });
  }
};


// ---------------------------------------------
// Mark notification as read
// ---------------------------------------------

const markNotificationAsRead = async (req, res) => {
  try {
    const notification =
      await Notification.findByIdAndUpdate(
        req.params.id,
        {
          isRead: true
        },
        {
          new: true
        }
      );

    if (!notification) {
      return res.status(404).json({
        success: false,
        message: "Notification not found"
      });
    }

    res.status(200).json({
      success: true,
      message: "Notification marked as read",
      data: notification
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to update notification",
      error: error.message
    });
  }
};


module.exports = {
  createNotification,
  getNotificationsByTemple,
  getUnreadNotifications,
  markNotificationAsRead
};