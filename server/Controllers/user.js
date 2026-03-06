const User = require("../models/user");
const jwt = require("jsonwebtoken");

// User Registration
exports.register = async (req, res) => {
  const { username, email, password, role } = req.body;
  try {
    // Validate Name and Email
    if (!/^[a-zA-Z\s]+$/.test(username)) {
      return res.status(400).json({ message: "Username/Full Name should only contain letters and spaces" });
    }
    if (!email.endsWith("@gmail.com")) {
      return res.status(400).json({ message: "Please use a @gmail.com address" });
    }

    // Check if user exists
    const existingUser = await User.findOne({ email });
    if (existingUser)
      return res
        .status(400)
        .json({ message: "User with this email already exists" });

    // Create new user
    const user = new User({ username, email, password, role });
    await user.save();

    res.status(201).json({ message: "User registered successfully" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// User Login
exports.login = async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user)
      return res.status(400).json({ message: "Invalid email or password" });

    // Compare password
    const isMatch = await user.comparePassword(password);
    if (!isMatch)
      return res.status(400).json({ message: "Invalid email or password" });

    // Generate tokens
    const tokens = user.generateTokens();

    // Set refresh token as HTTP-only cookie
    res.cookie("refreshToken", tokens.refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "Strict",
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    res.json({ accessToken: tokens.accessToken });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Logout - clear refresh token cookie
exports.logout = (req, res) => {
  res.clearCookie("refreshToken", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "Strict",
  });
  res.json({ message: "Logged out successfully" });
};

// Protected Profile - requires auth middleware
exports.profile = async (req, res) => {
  try {
    const user = await User.findById(req.userId).select("-password");
    if (!user) return res.status(404).json({ message: "User not found" });
    console.log(user);
    res.json(user);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Refresh access token using refresh token cookie
exports.refreshToken = (req, res) => {
  const refreshToken = req.cookies.refreshToken;
  if (!refreshToken)
    return res.status(401).json({ message: "No refresh token, login again" });

  try {
    const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
    const tokens = jwt.sign(
      { userId: payload.userId },
      process.env.JWT_SECRET,
      { expiresIn: "15m" }
    );
    // Optionally regenerate refresh token here as well

    res.json({ accessToken: tokens });
  } catch (err) {
    res.status(403).json({ message: "Invalid refresh token, login again" });
  }
};
