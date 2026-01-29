import joblib
import os
import numpy as np
import tempfile
from flask import current_app
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
def predict_crop_task(self, n, p, k, temperature, humidity, ph, rainfall, user_id=None):
    """
    Async task for crop prediction.
    Returns the predicted crop name.
    """
    try:
        model, encoder = load_crop_models()
        
        data = [
            float(n), float(p), float(k),
            float(temperature), float(humidity),
            float(ph), float(rainfall),
        ]
        
        prediction = model.predict([data])[0]
        crop = encoder.inverse_transform([prediction])[0]
        
        if user_id:
            NotificationService.create_notification(
                title="Crop Prediction Ready",
                message=f"The AI has recommended {crop} for your farm.",
                notification_type="task_completed",
                user_id=user_id
            )
        
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
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.process_loan')
def process_loan_task(self, json_data, user_id=None):
    """
    Async task for loan processing with Gemini API and PDF generation.
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
        
        # Trigger PDF Synthesis Task
        synthesize_loan_pdf_task.delay(json_data, reply, user_id)
        
        if user_id:
            NotificationService.create_notification(
                title="Loan Analysis Complete",
                message="Your loan eligibility analysis is ready. We are generating your PDF report now.",
                notification_type="loan_update",
                user_id=user_id
            )
        
        return {
            'status': 'success',
            'result': reply
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.synthesize_loan_pdf')
def synthesize_loan_pdf_task(self, user_data, analysis_result, user_id=None):
    """
    Generates a PDF report, saves it, and notifies the user.
    """
    try:
        # 1. Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        
        # 2. Generate PDF
        success = PDFService.generate_loan_report(user_data, analysis_result, tmp_path)
        
        if not success:
            raise Exception("PDF generation failed in service")
        
        # 3. Save to FileService (handles storage backend)
        with open(tmp_path, 'rb') as f:
            # Mocking a Flask-like file object for FileService
            class MockFile:
                def __init__(self, stream, filename):
                    self.stream = stream
                    self.filename = filename
                    self.content_type = 'application/pdf'
                def save(self, path):
                    with open(path, 'wb') as dest:
                        dest.write(self.stream.read())
                def seek(self, *args):
                    self.stream.seek(*args)
                def tell(self):
                    return self.stream.tell()

            mock_file = MockFile(f, f"Loan_Report_{datetime.now().strftime('%Y%m%d')}.pdf")
            file_record, error = FileService.save_file(mock_file, user_id=user_id)
            
            if error:
                raise Exception(f"File storage failed: {error}")

        # 4. Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
        # 5. Notify user
        if user_id:
            NotificationService.create_notification(
                title="PDF Report Ready",
                message=f"Your professional loan eligibility report ({file_record.original_name}) is now available for download.",
                notification_type="loan_update",
                user_id=user_id
            )
            
        return {'status': 'success', 'file_id': file_record.id}
    except Exception as e:
        logger.error(f"Async PDF synthesis failed: {str(e)}")
        if user_id:
            NotificationService.create_notification(
                title="Report Generation Failed",
                message="We encountered an error while generating your PDF report. Please try again later.",
                notification_type="system",
                user_id=user_id
            )
        return {'status': 'error', 'message': str(e)}
