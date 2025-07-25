# AgriTech

A unified Flask-based platform for crop recommendation, yield prediction, and plant disease detection.

---

## 🌾 Introduction
AgriTech is an all-in-one web platform designed to empower farmers, agri-entrepreneurs, and researchers with AI-powered tools for smarter agriculture. The platform integrates:
- Crop recommendation based on soil and weather
- Crop yield prediction using ML models
- Plant disease detection via deep learning
- Community features for farmers and shopkeepers

## 🚀 Features
- **Crop Recommendation:** Suggests the best crops to cultivate based on soil nutrients and climate.
- **Crop Yield Prediction:** Predicts expected yield for different crops using advanced ML models.
- **Plant Disease Detection:** Upload plant images to detect diseases and get treatment advice.
- **Farmer Portal:** Connect, share, and learn with other farmers.
- **Shopkeeper Listings:** Find local agri-product and equipment suppliers.
- **Community Chat:** Real-time chat for knowledge sharing.
- **Plantation Guidance:** Step-by-step guides for sustainable farming.

## 🖥️ Demo
> _Add screenshots or a link to a live demo here if available._

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
# Clone this repo and navigate to the project directory
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

### 4. Run the Flask App
```bash
cd AgriTech
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

## 📡 API Endpoints (Sample)
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
  app.py                # Unified Flask app
  templates/            # All HTML templates
  static/               # All static files (css, js, images)
  Crop_Recommendation/  # Crop recommendation blueprint
  Crop_Yield_Prediction/# Crop yield prediction blueprint
  Disease_prediction/   # Disease prediction blueprint
  ...
requirements.txt        # Python dependencies
.gitignore              # Files/folders ignored by git
```

## 📝 .gitignore
- Ignores virtual environments, model files, uploads, and other non-essential files.

## 💡 Notes
- Model files (`*.h5`, `*.pkl`, etc.) and uploads are not tracked in git for security and size reasons.
- For development, ensure you have the required model files in the correct locations.

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
Happy farming! 🌱

