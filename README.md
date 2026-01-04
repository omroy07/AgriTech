# 🌱 AgriTech: Smart Farming Solutions

[![SWoC 2026](https://img.shields.io/badge/SWoC-2026-blue?style=for-the-badge)](https://swoc.tech)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

**AgriTech** is an innovative AI-powered platform designed to empower farmers and agricultural communities with real-time insights, disease detection, and interactive collaboration tools to ensure a sustainable future.

---

## 🚀 Quick Start (TL;DR)
1. **Clone:** `git clone https://github.com/omroy07/AgriTech.git`
2. **Backend:** `pip install -r requirements.txt && python src/backend/app.py`
3. **Frontend:** Open `http://localhost:8000` after running a local server in `src/frontend/`.
4. **Goal:** Get accurate soil analysis and plant health reports instantly.

---

## 🎯 Quick Preview

### Dashboard Overview
![AgriTech Dashboard](https://github.com/omroy07/AgriTech/blob/main/image/Screenshot%202025-06-03%20111019.png)

### 📸 Key Features in Action

| Crop Recommendation | Disease Detection | Community Chat |
| :---: | :---: | :---: |
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

## 📂 Project Structure (Simplified)
```text
AGRITECH/
├── 📁 src/
│   ├── 📁 frontend/      # UI logic: HTML, CSS, and Client-side JS
│   │   ├── 📁 pages/     # HTML files for Dashboard, Crop, & Disease pages
│   │   └── 📁 assets/    # Local icons and data samples
│   ├── 📁 backend/       # Flask API: Routes and Server-side logic
│   │   ├── app.py        # Main entry point for the Backend
│   │   └── 📁 routes/    # Specific API endpoints (Crop, User, etc.)
│   └── 📁 ml_models/     # The "Brain" of AgriTech: AI/ML model files
│       ├── model.h5      # Pre-trained Deep Learning models
│       └── model.pkl     # Pre-trained Scikit-Learn models
├── 📁 images/            # Screenshots, GIFs, and Logos used in README
├── 📄 requirements.txt   # Python dependencies (Must install for ML)
└── 📄 README.md          # Main Documentation
```

---

## 🛡️ Security & Reliability

* **Data Sanitization:** All user-uploaded images are processed via **OpenCV** filters to ensure data integrity and prevent malicious file injections during the ML inference phase.
* **Environment Safety:** Sensitive information, including API keys, database credentials, and secret tokens, are strictly managed via `.env` files to prevent accidental exposure in the version control system.
* **Model Validation:** We implement continuous testing and cross-validation of our ML models (CNNs & Random Forest) to ensure a prediction accuracy threshold of **90% or above** before deployment.

---

## 🏁 Getting Started 

### 📋 Prerequisites
* **Python 3.9+**
* **Node.js 18+**
* **Local Server** (Live Server extension or Python `http.server`)

### ⚙️ Installation
```bash
git clone [https://github.com/omroy07/AgriTech.git](https://github.com/omroy07/AgriTech.git)
cd AgriTech
```

### 🐍 Running Backend
```bash
cd src/backend
pip install -r requirements.txt
python app.py
```

### 🌐 Running Frontend
```bash
cd src/frontend
python -m http.server 8000
# The application will be live at http://localhost:8000
```
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

| Name | Role |
| :--- | :--- |
| **Om Roy** | Project Lead | Web Developer | ML Engineer |
| **Kanisha Ravindra Sharma** | ML Engineer | Backend Developer |
| **Shubhangi Roy** | ML Engineer | Backend Developer |

---

---

## 🤝 Contributing & Support

We love contributions! Please read our **[CONTRIBUTING.md](./CONTRIBUTING.md)** to get started with **SWoC 2026** tasks. Whether it's fixing bugs, adding features, or improving documentation, your help is always welcome!

---

## ✨ Contributors

#### Thanks to all the wonderful people contributing to this project! 💖

<a href="https://github.com/omroy07/AgriTech/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=omroy07/AgriTech" />
</a>

#### [View full contribution graph](https://github.com/omroy07/AgriTech/graphs/contributors)

---

<div align="center">
  <b>Made with ❤️ by the AgriTech Community. Part of SWoC 2026.</b>
</div>
