const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const connectDB = require("./config/db");

dotenv.config();

const app = express();

// Connect MongoDB
connectDB();

// Middleware
app.use(cors());
app.use(express.json());

// Test route
app.get("/", (req, res) => {
  res.json({
    success: true,
    message: "TirthaSetu Backend is running successfully"
  });
});
app.use("/api/temples", require("./routes/templeRoutes"));
app.use("/api/crowd", require("./routes/crowdRoutes"));
app.use("/api/bookings", require("./routes/bookingRoutes"));
app.use("/api/parking", require("./routes/parkingRoutes"));
app.use("/api/emergency", require("./routes/emergencyRoutes"));
app.use("/api/sensors", require("./routes/sensorRoutes"));
app.use("/api/prediction", require("./routes/predictionRoutes"));
app.use("/api/resources",require("./routes/resourceRoutes"));
app.use("/api/traffic",require("./routes/trafficRoutes"));
app.use("/api/notifications",require("./routes/notificationRoutes"));

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`TirthaSetu Backend running on port ${PORT}`);
});