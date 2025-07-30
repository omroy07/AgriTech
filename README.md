# AgriTech

A unified Flask-based platform for crop recommendation, yield prediction, and plant disease detection.

---

## 🌾 Introduction

AgriTech is an all-in-one web platform designed to empower farmers, agri-entrepreneurs, and researchers with AI-powered tools for smarter agriculture. The platform integrates:

- **Crop Recommendation:** Suggests the best crops to cultivate based on soil nutrients and climate.
- **Crop Yield Prediction:** Predicts expected yield for different crops using advanced ML models.
- **Plant Disease Detection:** Upload plant images to detect diseases and get treatment advice.
- **Community Features:** Farmer portal, shopkeeper listings, and real-time chat for knowledge sharing.

---

## 🚀 Features

- **Crop Recommendation:** Get suggestions for the most suitable crops based on soil and weather data.
- **Crop Yield Prediction:** Estimate expected crop yield using machine learning models.
- **Plant Disease Detection:** Upload plant images to detect diseases and receive treatment recommendations.
- **Farmer Portal:** Connect, share, and learn with other farmers.
- **Shopkeeper Listings:** Find local agri-product and equipment suppliers.
- **Community Chat:** Real-time chat for knowledge sharing.
- **Plantation Guidance:** Step-by-step guides for sustainable farming.

---

## 🖥️ Demo

> _Add screenshots or a link to a live demo here if available._

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AgriTech.git
cd AgriTech
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download/Place Model Files

- Place the required model files (`*.pkl`, `*.h5`, etc.) in the respective `model/` or `models/` folders inside each module directory.

### 5. Run the Flask App

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📦 Usage

- Access the homepage for navigation to all modules.
- Use the Crop Recommendation and Yield Prediction forms to get AI-powered suggestions.
- Upload plant images in the Disease Detection module for instant analysis.
- Use the Farmer and Shopkeeper portals for community features.

---

## 📡 API Endpoints

- `/crop-recommendation/` : Crop recommendation form
- `/crop-recommendation/predict` : POST endpoint for crop prediction
- `/crop-yield/` : Crop yield prediction form
- `/crop-yield/predict` : POST endpoint for yield prediction
- `/disease/` : Plant disease detection form
- `/disease/predict` : POST endpoint for disease prediction

---

## 📁 Project Structure

```
AgriTech/
  app.py                      # Unified Flask app
  requirements.txt            # Python dependencies
  templates/                  # Shared HTML templates
  static/                     # Shared static files (css, js, images)
  Crop_Recommendation/
    crop_recommendation_blueprint.py
    model/                    # Crop recommendation model files
    templates/                # Crop recommendation templates
    static/                   # Crop recommendation static files
  Crop_Yield_Prediction/
    crop_yield_app/
      crop_yield_blueprint.py
      model/                  # Crop yield model files
      templates/              # Crop yield templates
      static/                 # Crop yield static files
  disease_prediction/
    disease_blueprint.py
    model/                    # Disease detection model files
    templates/                # Disease detection templates
    static/                   # Disease detection static files
  ...
.gitignore                    # Files/folders ignored by git
```

---

## 📝 .gitignore

- Ignores virtual environments, model files, uploads, and other non-essential files.
- Example:
  ```
  venv/
  __pycache__/
  *.pyc
  *.pkl
  *.h5
  uploads/
  ```

---

## 💡 Notes

- Model files (`*.h5`, `*.pkl`, etc.) and uploads are not tracked in git for security and size reasons.
- For development, ensure you have the required model files in the correct locations.
- Each module may have its own requirements for input data and model files.

---

## 🔄 How to update requirements.txt

If you add new packages to your virtual environment, update `requirements.txt` with:

```bash
pip freeze > requirements.txt
```

This ensures all dependencies are tracked for deployment and collaboration.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

Please read `CONTRIBUTING.md` for more details.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

---

## ❓ FAQ

**Q: Where do I put my model files?**  
A: Place them in the respective `model/` or `models/` folders as described in each module's README or docstring.

**Q: How do I add a new module?**  
A: Create a new Flask blueprint, add it to `app.py`, and follow the project structure.

**Q: Who do I contact for support?**  
A: Open an issue on GitHub or contact the maintainers listed in the repository.

---

## 🚀 How to Push Your Code to GitHub

1. **Initialize git (if not already):**
   ```bash
   git init
   ```

2. **Add your remote repository:**
   ```bash
   git remote add origin https://github.com/ShaanifFaqui/AgriTech.git
   ```

3. **Check status and add files:**
   ```bash
   git status
   git add .
   ```

4. **Commit your changes:**
   ```bash
   git commit -m "Your commit message"
   ```

5. **Push to GitHub (main branch):**
   ```bash
   git branch -M main
   git push -u origin main
   ```

If you are pushing for the first time, you may be prompted to log in or use a token.

---
Happy farming! 🌱

