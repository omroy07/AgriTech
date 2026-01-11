# 🌱 AgriTech: Smart Farming Solutions

[![SWoC 2026](https://img.shields.io/badge/SWoC-2026-blue?style=for-the-badge)](https://swoc.tech)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

**AgriTech** is an innovative AI-powered platform designed to empower farmers and agricultural communities with real-time insights, disease detection, and interactive collaboration tools to ensure a sustainable future.

---

## 🚀 Quick Start (TL;DR)

1. **Clone:** `git clone https://github.com/omroy07/AgriTech.git && cd AgriTech`
2. **Install & Run Backend:** `pip install -r requirements.txt && python app.py` (runs on `http://localhost:5000`)
3. **Run Frontend:** In another terminal: `cd src/frontend && python -m http.server 8000` (opens `http://localhost:8000`)
4. **Goal:** Get accurate soil analysis and plant health reports instantly.

> **Note:** Backend handles APIs; Frontend is the web UI. Both must run together.

---

## 🎯 Quick Preview

### Dashboard Overview

![AgriTech Dashboard](https://github.com/omroy07/AgriTech/blob/main/image/Screenshot%202025-06-03%20111019.png)

### 📸 Key Features in Action

|                                           Crop Recommendation                                            |                                          Disease Detection                                           |                                         Community Chat                                         |
| :------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------: |
| ![Crop Recommendation](https://github.com/omroy07/AgriTech/raw/main/images/gifs/crop-recommendation.gif) | ![Disease Detection](https://github.com/omroy07/AgriTech/raw/main/images/gifs/disease-detection.gif) | ![Community Chat](https://github.com/omroy07/AgriTech/raw/main/images/gifs/community-chat.gif) |

---

## 🏗 System Architecture & Flow

1. **User Input:** Farmers upload soil data or plant images via the Dashboard.
2. **Processing:** The Flask backend routes data to specific AI/ML models.
3. **ML Inference:**
   - **CNN Models:** Detect plant diseases from images.
   - **Random Forest/XGBoost:** Suggest crops based on soil NPK levels.
4. **Output:** Results are displayed with preventive measures and yield predictions.

---

## 🌟 Core Features

- 🌾 **Crop Recommendation:** AI suggestions based on soil and weather.
- 📉 **Yield Prediction:** Advanced models to forecast seasonal harvest.
- 🔬 **Disease Prediction:** Early detection of plant diseases with treatment steps.
- 🤝 **Farmer Connection:** A community hub to share resources and advice.
- 🛒 **Shopkeeper Listings:** Local directory for agricultural products.

---

## 🛠 Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Backend:** Flask (Python) / Node.js
- **Machine Learning:** TensorFlow, Scikit-Learn, OpenCV
- **Database:** MySQL / MongoDB
- **DevOps:** Docker, GitHub Actions (CI/CD)

---

## 📂 Project Structure

```text
AGRITECH/
├── app.py                      # 🐍 Flask Backend (Main entry point)
├── server.js                   # 🟢 Node.js Server (Optional)
├── requirements.txt            # Python dependencies
├── firebase.js                 # Firebase config fetching
├── 📁 src/
│   └── 📁 frontend/            # 🌐 Frontend UI (HTML, CSS, JS)
│       ├── 📁 pages/           # Individual page files
│       ├── 📁 css/             # Stylesheets
│       └── 📁 js/              # Client-side scripts
├── 📁 Crop Recommendation/     # 🌾 Crop recommendation module
├── 📁 Disease prediction/      # 🔬 Disease detection module
├── 📁 Crop Yield Prediction/   # 📊 Yield forecasting module
├── 📁 Community/               # 💬 Community/forum backend
├── 📁 images/                  # 📸 Screenshots and assets
├── 📄 README.md                # This file
└── 📄 CONTRIBUTING.md          # Contribution guidelines
```

### Backend vs Frontend

- **Backend** (`app.py` at root): Flask server handling APIs, Firebase config, loan processing
- **Frontend** (`src/frontend/`): Static HTML/CSS/JS served via Python HTTP server
- **Optional Node Server** (`server.js`): Alternative chat backend (not required)

---

## 🛡️ Security & Reliability

- **Data Sanitization:** All user-uploaded images are processed via **OpenCV** filters to ensure data integrity and prevent malicious file injections during the ML inference phase.
- **Environment Safety:** Sensitive information, including API keys, database credentials, and secret tokens, are strictly managed via `.env` files to prevent accidental exposure in the version control system.
- **Model Validation:** We implement continuous testing and cross-validation of our ML models (CNNs & Random Forest) to ensure a prediction accuracy threshold of **90% or above** before deployment.

---

## 🏁 Getting Started

### 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Local Server** (Live Server extension or Python `http.server`)

### ⚙️ Installation

```bash
git clone [https://github.com/omroy07/AgriTech.git](https://github.com/omroy07/AgriTech.git)
cd AgriTech
```

### 🐍 Running Backend (Flask)

```bash
# From project root
pip install -r requirements.txt

# Set environment variables (create .env file or export)
export GEMINI_API_KEY="your_api_key_here"
export FIREBASE_API_KEY="your_firebase_key"
# ... (see .env.example for all required vars)

# Start Flask server
python app.py
# Backend runs on http://localhost:5000
```

### 🌐 Running Frontend (Static Server)

```bash
# In a NEW terminal, from project root
cd src/frontend
python -m http.server 8000
# Frontend runs on http://localhost:8000
```

### ✅ Verify Both Are Running

- Backend API: http://localhost:5000/ (JSON response)
- Frontend UI: http://localhost:8000/ (HTML page)
- Open http://localhost:8000 in your browser

### 📝 Setting Up Environment Variables

Create a `.env` file at project root:

```
GEMINI_API_KEY=your_gemini_key
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_bucket.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id
```

See `.env.example` for a template.

## 🛣 Roadmap

- [ ] Cloud deployment
- [ ] Mobile app integration
- [ ] Real-time weather API
- [ ] AI chatbot for farmers
- [ ] Regional language support

## 🔄 Contribution Flow

Fork → Clone → Branch → Code → Commit → Push → Pull Request → Review → Merge

---

## 🔮 Future Scope

- **Cloud Deployment:** Migration to AWS/Heroku for global high-availability.
- **Mobile Integration:** Native Android application for on-field utility.
- **IoT Support:** Integration with real-time soil moisture and NPK sensors.
- **Multilingual Support:** Adding regional Indian languages to improve accessibility for farmers.

---

## 👥 Team Members

| Name                        | Role         |
| :-------------------------- | :----------- | ----------------- | ----------- |
| **Om Roy**                  | Project Lead | Web Developer     | ML Engineer |
| **Kanisha Ravindra Sharma** | ML Engineer  | Backend Developer |
| **Shubhangi Roy**           | ML Engineer  | Backend Developer |

---

---

## 🤝 Contributing & Support

We love contributions! Please read our **[CONTRIBUTING.md](./CONTRIBUTING.md)** to get started with **SWoC 2026** tasks. Whether it's fixing bugs, adding features, or improving documentation, your help is always welcome!

---

## ✨ Contributors
wahide

#### Thanks to all the wonderful people contributing to this project! 💖

<a href="https://github.com/omroy07/AgriTech/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=omroy07/AgriTech" />
</a>

#### [View full contribution graph](https://github.com/omroy07/AgriTech/graphs/contributors)

---

<div align="center">
  <b>Made with ❤️ by the AgriTech Community. Part of SWoC 2026.</b>
</div>
