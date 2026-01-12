# AgriTech Project - Quick Start Guide

## ✅ Dependencies Installed

All Python dependencies from requirements.txt are installed in the virtual environment at `.venv/`

## 🚀 Running the Project

### Start Backend (Flask API)

```powershell
.\start_backend.ps1
```

**Backend URL:** http://localhost:5000

### Start Frontend (Static Server)

```powershell
python -m http.server 8080
```

**Frontend URL:** http://localhost:8080

## 📝 Configuration

Environment variables are stored in `.env` file:

- `GEMINI_API_KEY` - Google Gemini API key
- `FIREBASE_*` - Firebase configuration

Update these values in `.env` file for production use.

## 🔍 Accessing the Application

- **Home Page:** http://localhost:8080/index.html
- **About:** http://localhost:8080/about.html
- **Blog:** http://localhost:8080/blog.html
- **Contact:** http://localhost:8080/contact.html
- **Firebase Config API:** http://localhost:5000/api/firebase-config

## ✨ Features

- ✓ All dependencies installed
- ✓ Virtual environment configured
- ✓ Environment variables set
- ✓ Backend Flask server running (port 5000)
- ✓ Frontend static server running (port 8080)
- ✓ Accessibility improvements applied (skip links, landmarks, proper headings)

## 🛠️ Project Structure

```
AgriTechSwoc/
├── app.py                 # Flask backend
├── start_backend.ps1      # Backend startup script
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── .venv/                 # Virtual environment
├── index.html            # Home page
├── about.html            # About page
├── blog.html             # Blog page
├── contact.html          # Contact page
└── ... (other pages)
```

## 🔧 Troubleshooting

If you encounter issues:

1. **Backend not starting:** Check `.env` file exists and has proper values
2. **Port conflicts:** Change ports in startup commands if 5000/8080 are in use
3. **Import errors:** Ensure virtual environment is activated: `.venv/Scripts/activate`

## 📦 Installed Packages

Key packages installed:

- Flask & Flask-CORS (Web framework)
- google-generativeai (AI integration)
- PyJWT & bcrypt (Security)
- TensorFlow, Keras, PyTorch (ML models)
- scikit-learn, xgboost, catboost (ML libraries)
- streamlit (Data apps)
- And 100+ more dependencies

---

**Project Status:** ✅ Running error-free
