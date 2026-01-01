# 🌾 AgriTech Web Application

AgriTech is an innovative web platform designed to empower farmers and agricultural communities with AI-powered tools, real-time insights, and interactive collaboration features.

---

## 🎯 Quick Preview

### Dashboard Overview
![AgriTech Dashboard](https://github.com/omroy07/AgriTech/blob/main/image/Screenshot%202025-06-03%20111019.png)

### Key Features in Action
| Crop Recommendation | Disease Detection | Community Chat |
|:-------------------:|:-----------------:|:--------------:|
| ![Crop Recommendation GIF](link-to-crop-recommendation.gif) | ![Disease Detection GIF](link-to-disease-detection.gif) | ![Community Chat GIF](link-to-community-chat.gif) |

---

## 🚀 Getting Started

### Prerequisites
- Web browser (Chrome, Firefox, Safari, or Edge)
- Local server (for full functionality)

### Quick Setup
1. *Clone the repository*
   ```bash
   git clone https://github.com/omroy07/AgriTech.git
   cd AgriTech
Run the application

Option A: Simple HTML Preview

```bash
# Open index.html in your browser
open index.html 
```
Option B: Local Server (Recommended)

```bash
# Using Python
python -m http.server 8000
Then visit http://localhost:8000
```

# Using Node.js
```npx serve
# Or install live-server: npm install -g live-server
```
- live-server
- Access the application

- Open your web browser
```
Navigate to http://localhost:8000 (or the port shown in terminal)
```

- Start exploring AgriTech features!

# For Development & Contribution
See our Contributing Guide for detailed setup instructions, coding standards, and pull request process.

🌟 Features
- Crop Recommendation
Get suggestions for the best crops to cultivate based on soil and weather conditions.

- Yield Prediction
Predict expected yields using advanced AI models tailored to different crop types.

- Disease Prediction
Early detection of plant diseases along with treatment and preventive measures.

- Farmer Connection
Connect with fellow farmers to share experiences, resources, and advice.

- Shopkeeper Listings
Discover local agricultural product and service providers.

# File Structure
AgriTech/\
├── 📁 docs/                        # Documentation files\ \
│   ├── CONTRIBUTING.md\
│   ├── TROUBLESHOOTING.md\
│   ├── API_DOCUMENTATION.md\
│   └── SETUP_GUIDE.md\
│
├── 📁 images/                        # All images and visual assets\
│   ├── screenshots/\
│   │   ├── dashboard.png\
│   │   ├── crop-recommendation.png\
│   │   ├── disease-detection.png\
│   │   └── community-chat.png\
│   │
│   ├── gifs/                         # Preview GIFs for README\
│   │   ├── crop-recommendation.gif\
│   │   ├── community-chat.gif\
│   │   └── yield-prediction.gif\
│   │
│   ├── icons/\
│   │   ├── favicon.ico\
│   │   ├── logo.png\
│   │   └── apple-touch-icon.png\
│   │
│   └── mockups/\
│       ├── mobile-view.png\
│       └── tablet-view.png\
│
├── 📁 src/                           # Main source code\
│   ├── 📁 frontend/\
│   │   ├── index.html                # Main entry point\
│   │   ├── 📁 css/\
│   │   │   ├── style.css\
│   │   │   ├── components/\
│   │   │   │   ├── navbar.css\
│   │   │   │   ├── sidebar.css\
│   │   │   │   ├── cards.css\
│   │   │   │   └── forms.css\
│   │   │   ├── pages/\
│   │   │   │   ├── dashboard.css\
│   │   │   │   ├── crop-recommendation.css\
│   │   │   │   ├── disease-detection.css\
│   │   │   │   └── community.css\
│   │   │   └── responsive.css\
│   │   │
│   │   ├── 📁 js/\
│   │   │   ├── app.js                # Main application logic\
│   │   │   ├── 📁 modules/\
│   │   │   │   ├── auth.js\
│   │   │   │   ├── utils.js\
│   │   │   │   └── animations.js\
│   │   │   ├── 📁 features/\
│   │   │   │   ├── crop-recommendation.js\
│   │   │   │   ├── yield-prediction.js\
│   │   │   │   ├── disease-detection.js\
│   │   │   │   └── community-chat.js\
│   │   │   └── 📁 components/\
│   │   │       ├── navbar.js\
│   │   │       ├── modal.js\
│   │   │       └── charts.js\
│   │   │
│   │   ├── 📁 assets/\
│   │   │   ├── 📁 fonts/\
│   │   │   ├── 📁 icons/             # SVG icons\
│   │   │   └── 📁 data/              # Sample data for demos\
│   │   │
│   │   └── 📁 pages/                 # HTML pages for different features\
│   │       ├── dashboard.html\
│   │       ├── crop-recommendation.html\
│   │       ├── yield-prediction.html\
│   │       ├── disease-detection.html\
│   │       ├── community.html\
│   │       ├── shopkeepers.html\
│   │       └── plantation-guide.html\
│   │
│   ├── 📁 backend/                   # Backend server code\
│   │   ├── app.py                   # Flask main application\
│   │   ├── requirements.txt\
│   │   ├── 📁 routes/\
│   │   │   ├── auth_routes.py\
│   │   │   ├── crop_routes.py\
│   │   │   ├── disease_routes.py\
│   │   │   ├── yield_routes.py\
│   │   │   └── community_routes.py\
│   │   ├── 📁 models/\
│   │   │   ├── user_model.py\
│   │   │   ├── crop_model.py\
│   │   │   ├── disease_model.py\
│   │   │   └── database.py\
│   │   ├── 📁 ml_models/             # AI/ML model files\
│   │   │   ├── crop_recommendation/\
│   │   │   │   ├── model.pkl\
│   │   │   │   ├── train_model.py\
│   │   │   │   └── preprocessing.py\
│   │   │   ├── yield_prediction/\
│   │   │   │   ├── model.h5\
│   │   │   │   ├── train_model.py\
│   │   │   │   └── data_processing.py\
│   │   │   └── disease_detection/\
│   │   │       ├── model.h5\
│   │   │       ├── train_model.py\
│   │   │       └── image_processing.py\
│   │   ├── 📁 utils/\
│   │   │   ├── helpers.py\
│   │   │   ├── validators.py\
│   │   │   └── constants.py\
│   │   └── 📁 config/\
│   │       ├── database.py\
│   │       └── settings.py\
│   │
│   └── 📁 database/                  # Database related files\
│       ├── schema.sql\
│       ├── sample_data.sql\
│       └── migrations/\
│
├── 📁 tests/                         # Test files\
│   ├── 📁 frontend/\
│   │   ├── unit/\
│   │   └── integration/\
│   ├── 📁 backend/\
│   │   ├── unit/\
│   │   └── integration/\
│   └── 📁 ml_models/\
│       ├── test_crop_model.py\
│       ├── test_yield_model.py\
│       └── test_disease_model.py\
│
├── 📁 scripts/                       # Utility scripts\
│   ├── setup.sh                      # Quick setup script\
│   ├── deploy.sh\
│   ├── backup_database.sh\
│   └── generate_gifs.py              # Script to create preview GIFs\
│
├── 📁 config/                        # Configuration files\
│   ├── environment.yml\
│   ├── nginx.conf\
│   └── gunicorn.conf.py\
│
├── 📁 .github/                       # GitHub workflows and templates\
│   ├── workflows/\
│   │   ├── ci-cd.yml\
│   │   └── deploy.yml\
│   ├── ISSUE_TEMPLATE/\
│   │   ├── bug_report.md\
│   │   └── feature_request.md\
│   └── PULL_REQUEST_TEMPLATE.md\
│
├── 📁 data/                          # Datasets and training data\
│   ├── 📁 crop_data/\
│   ├── 📁 disease_images/\
│   └── 📁 yield_data/\
│
├── 📁 logs/                          # Application logs\
│   ├── app.log\
│   ├── error.log\
│   └── access.log\
│
├── 📄 .env.example                   # Environment variables template\
├── 📄 .gitignore\
├── 📄 README.md                      # Main documentation\
├── 📄 package.json                   # Node.js dependencies (if using Node)\
├── 📄 requirements.txt               # Python dependencies\
├── 📄 Dockerfile                    # Container configuration\
├── 📄 docker-compose.yml             # Multi-container setup\
└── 📄 LICENSE                        # Project license\

# Community Chat
Collaborate and discuss challenges, share solutions, and keep up with the latest in agriculture.

Plantation Guidance
Access helpful plantation techniques and strategies for better crop growth.

Crop Planning
Plan your season with confidence and unlock your farm's true potential for a more profitable and sustainable future.

# 🛠 Technologies Used
- Frontend: HTML, CSS, JavaScript

- Backend: Flask / Node.js

- AI/ML Models: For prediction modules (Crop, Yield, Disease)

- Database: MySQL / MongoDB

- Hosting: Localhost (127.0.0.1), with option for cloud deployment

# 👥 Team Members & Roles
- Om Roy – Project Lead & Web Developer & Machine Learning Engineer

- Kanisha Ravindra Sharma – Machine Learning Engineer & Backend Developer

- Shubhangi Roy – Machine Learning Engineer & Backend Developer

# 🤝 Contributing
We welcome contributions! Please read our Contributing Guide to get started. It includes:

Setting up the development environment

Code style guidelines

How to submit pull requests

Reporting issues

# First time contributing? Check out our Good First Issues!

🌐 Future Scope
☁ Cloud deployment (e.g., Vercel, Heroku)

📱 Mobile app integration

🌦 Real-time weather API

🤖 AI chatbot for agriculture support

🗣 Support for regional languages

📞 Support
If you encounter any issues:

Check the Troubleshooting Guide

Search existing Issues

Create a new issue with details about your problem

📄 License
This project is licensed under the MIT License.

text

## Additional Files to Create

### 1. CONTRIBUTING.md
markdown
# Contributing to AgriTech

Thank you for your interest in contributing to AgriTech! Here's how you can help:

## Development Setup

1. *Fork the repository*
2. *Clone your fork*
   ```bash
   git clone https://github.com/your-username/AgriTech.git
   cd AgriTech
   ```
Set up development environment

```bash
# Install dependencies (if any)
npm install
# or
pip install -r requirements.txt
Start development server
```

```bash
npm run dev
# or
python app.py
Making Changes
Create a new branch:
```

```bash
git checkout -b feature/your-feature-name
Make your changes and test thoroughly

Commit your changes:
```

```bash
git commit -m "Add: description of your changes"
Push to your fork:
```

```bash
git push origin feature/your-feature-name
Create a Pull Request
```

# Code Style
- Use meaningful variable names

- Comment complex logic

- Follow existing code formatting

- Test your changes across different browsers

# Need Help?
- Join our discussions in Issues

- Contact maintainers for guidance

- text

### 2. TROUBLESHOOTING.md
markdown
# Troubleshooting Guide

## Common Issues

### Page not loading?
- Ensure you're running a local server, not just opening HTML files directly
- Check if port 8000 is available, try a different port if needed

### Features not working?
- Check browser console for errors (F12 → Console)
- Ensure all dependencies are installed
- Verify your browser supports ES6+ features

### Images/GIFs not loading?
- Check file paths are correct
- Ensure images are in the correct directory
- Verify file permissions

## Getting Help
1. Check this guide
2. Search existing issues
3. Create a new issue with:
   - Your browser and version
   - Error messages from console
   - Steps to reproduce the issue
For Creating Preview GIFs
You can create the suggested GIFs using:

# Screen recording tools:

Windows: ScreenToGif, OBS Studio

Mac: QuickTime Player, GIPHY Capture

Linux: Peek, OBS Studio

Recommended workflow:

Record 5-10 second clips of key features

Optimize file size (keep under 5MB)

Show the most valuable interactions

Add to an /images or /gifs folder in your repo


## ✨ Contributors
wahide

#### Thanks to all the wonderful contributors 💖

<a href="https://github.com/omroy07/AgriTech/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=omroy07/AgriTech" />
</a>

#### See full list of contributor contribution [Contribution Graph](https://github.com/omroy07/AgriTech/graphs/contributors)  
