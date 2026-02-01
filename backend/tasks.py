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


@celery_app.task(bind=True, name='tasks.verify_claim_with_ai')
def verify_claim_with_ai_task(self, claim_id):
    """
    Async task for AI-powered insurance claim verification using Gemini Vision API.
    Analyzes evidence photos to verify crop damage claims.
    """
    try:
        from backend.models import db, ClaimRequest
        import google.generativeai as genai
        
        claim = ClaimRequest.query.get(claim_id)
        if not claim:
            return {'status': 'error', 'message': f'Claim {claim_id} not found'}
        
        # Update status to under review
        claim.ai_verification_status = 'UNDER_REVIEW'
        claim.status = 'UNDER_REVIEW'
        db.session.commit()
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            claim.ai_verification_status = 'MANUAL_REVIEW'
            claim.ai_verification_notes = 'API key not configured - requires manual review'
            db.session.commit()
            return {'status': 'error', 'message': 'GEMINI_API_KEY not configured'}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Analyze evidence photos
        if not claim.evidence_photos or len(claim.evidence_photos) == 0:
            claim.ai_verification_status = 'MANUAL_REVIEW'
            claim.ai_verification_confidence = 0.0
            claim.ai_verification_notes = 'No evidence photos provided - requires manual review'
            db.session.commit()
            
            NotificationService.create_notification(
                title="Claim Under Manual Review",
                message=f"Your claim {claim.claim_number} requires manual review due to missing evidence.",
                notification_type="insurance",
                user_id=claim.user_id
            )
            return {'status': 'manual_review', 'reason': 'No evidence photos'}
        
        # Build prompt for Gemini
        prompt = f"""
You are an agricultural insurance claims assessor specializing in crop damage verification.

CLAIM DETAILS:
- Claim Number: {claim.claim_number}
- Claimed Amount: ₹{claim.claimed_amount}
- Incident Date: {claim.incident_date}
- Incident Description: {claim.incident_description}

TASK:
Analyze the provided evidence photographs and determine:
1. Whether the damage is consistent with the description
2. Estimated severity of damage (0-100%)
3. Whether the claim appears legitimate
4. Any red flags or concerns

Respond in this EXACT JSON format:
{{
    "verdict": "VERIFIED" or "REJECTED" or "MANUAL_REVIEW",
    "confidence": 0.85,
    "damage_severity": 65,
    "findings": "Brief description of what you observed",
    "concerns": "Any red flags or concerns (or 'None')"
}}

NOTE: Evidence photos are described below. In production, actual images would be analyzed.
Photo URLs: {', '.join(claim.evidence_photos)}
"""
        
        # In production, you would pass actual images to the Vision API
        # For now, we simulate with text analysis
        response = model.generate_content(prompt)
        
        if not response.candidates:
            claim.ai_verification_status = 'MANUAL_REVIEW'
            claim.ai_verification_notes = 'AI analysis inconclusive'
            db.session.commit()
            return {'status': 'error', 'message': 'No response from AI'}
        
        ai_result = response.candidates[0].content.parts[0].text
        
        # Parse AI response (simplified - in production, use proper JSON parsing)
        import re
        import json
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_result, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                
                verdict = analysis.get('verdict', 'MANUAL_REVIEW')
                confidence = float(analysis.get('confidence', 0.5))
                findings = analysis.get('findings', 'Analysis completed')
                concerns = analysis.get('concerns', '')
                
                claim.ai_verification_status = verdict
                claim.ai_verification_confidence = confidence
                claim.ai_verification_notes = f"{findings}\nConcerns: {concerns}"
                
                # If confidence is low, flag for manual review
                if confidence < 0.7:
                    claim.ai_verification_status = 'MANUAL_REVIEW'
                
                db.session.commit()
                
                # Notify user
                if verdict == 'VERIFIED':
                    message = f"Good news! Your claim {claim.claim_number} has been verified by our AI system and is being processed."
                    notif_type = "insurance"
                elif verdict == 'REJECTED':
                    message = f"Your claim {claim.claim_number} could not be automatically verified. Our team will review it manually."
                    notif_type = "insurance"
                else:
                    message = f"Your claim {claim.claim_number} is under manual review by our team."
                    notif_type = "insurance"
                
                NotificationService.create_notification(
                    title="Claim Verification Update",
                    message=message,
                    notification_type=notif_type,
                    user_id=claim.user_id
                )
                
                return {
                    'status': 'success',
                    'claim_id': claim_id,
                    'verdict': verdict,
                    'confidence': confidence
                }
            else:
                raise ValueError("Could not parse AI response")
                
        except Exception as parse_error:
            logger.error(f"Failed to parse AI response: {str(parse_error)}")
            claim.ai_verification_status = 'MANUAL_REVIEW'
            claim.ai_verification_notes = f'AI response parsing failed: {str(parse_error)}'
            db.session.commit()
            return {'status': 'error', 'message': str(parse_error)}
        
    except Exception as e:
        logger.error(f"AI claim verification failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.recalculate_risk_scores')
def recalculate_risk_scores_task(self, user_ids=None):
    """
    Periodic task to recalculate risk scores for all users or specific users.
    Typically run daily or weekly via Celery Beat.
    """
    try:
        from backend.models import User
        from backend.services.risk_service import RiskService
        
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
        else:
            users = User.query.all()
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                RiskService.calculate_user_risk_score(
                    user_id=user.id,
                    force_recalculate=True
                )
                success_count += 1
            except Exception as user_error:
                logger.error(f"Failed to recalculate score for user {user.id}: {str(user_error)}")
                error_count += 1
        
        return {
            'status': 'success',
            'processed': success_count + error_count,
            'success': success_count,
            'errors': error_count
        }
        
    except Exception as e:
        logger.error(f"Risk score recalculation task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}
