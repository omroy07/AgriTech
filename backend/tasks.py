import joblib
import os
import numpy as np
from backend.celery_app import celery_app
from backend.utils.i18n import t

# Load models at worker startup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CROP_MODEL_PATH = os.path.join(BASE_DIR, "crop_recommendation", "model", "rf_model.pkl")
CROP_ENCODER_PATH = os.path.join(BASE_DIR, "crop_recommendation", "model", "label_encoder.pkl")

# Global model references (loaded once per worker)
crop_model = None
crop_encoder = None


def load_crop_models():
    """Load crop prediction models."""
    global crop_model, crop_encoder
    if crop_model is None:
        crop_model = joblib.load(CROP_MODEL_PATH)
        crop_encoder = joblib.load(CROP_ENCODER_PATH)
    return crop_model, crop_encoder


@celery_app.task(bind=True, name='tasks.predict_crop')
def predict_crop_task(self, n, p, k, temperature, humidity, ph, rainfall):
    """
    Async task for crop prediction.
    Returns the predicted crop name.
    """
    try:
        model, encoder = load_crop_models()
        
        data = [
            float(n),
            float(p),
            float(k),
            float(temperature),
            float(humidity),
            float(ph),
            float(rainfall),
        ]
        
        prediction = model.predict([data])[0]
        crop = encoder.inverse_transform([prediction])[0]
        
        return {
            'status': 'success',
            'prediction': crop,
            'input_params': {
                'N': n, 'P': p, 'K': k,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@celery_app.task(bind=True, name='tasks.process_loan')
def process_loan_task(self, json_data):
    """
    Async task for loan processing with Gemini API.
    """
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return {'status': 'error', 'message': 'GEMINI_API_KEY not configured'}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
You are a financial loan eligibility advisor specializing in agricultural loans for farmers in India.
JSON Data = {json_data}
Analyze the farmer's provided details and assess their loan eligibility.
Respond in a structured format with labeled sections: Loan Type, Eligibility Status, Loan Range, Improvements, Schemes.
"""
        
        response = model.generate_content(prompt)
        
        if not response.candidates:
            return {'status': 'error', 'message': 'No response generated from Gemini API'}
        
        reply = response.candidates[0].content.parts[0].text
        
        return {
            'status': 'success',
            'result': reply
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
