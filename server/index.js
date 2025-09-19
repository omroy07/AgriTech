require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const cookieParser = require("cookie-parser");
const cors = require("cors");
const helmet = require("helmet");
const authRoutes = require("./Routes/user.js");
const connectDB = require("./config/db");

const app = express();

// Security HTTP headers
app.use(helmet());

// Enable CORS for all origins in development
//just for development purpose
// In production, configure it to allow only your frontend domains
app.use(
  cors({
    origin: "*",
    credentials: true,
  })
);

app.use(express.json());
app.use(cookieParser());

// Connect to MongoDB
connectDB();

// Mount auth routes
app.use("/api/auth", authRoutes);

// Basic error handler middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: "Server Error" });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
sendEmail = require("./Utils/email.js");
// Test email sending on server start
(async () => {
  const emailSent = await sendEmail(
    "pidugubunny534@gmail.com",
    "Test Email from AgriTech",
    "<h1>This is a test email</h1><p>If you received this, email setup is working!</p>"
  );
  console.log("Test email sent:", emailSent);
})();
