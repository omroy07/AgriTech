import joblib
import os
import numpy as np
import tempfile
from datetime import datetime
from flask import current_app
from backend.celery_app import celery_app
from backend.services.pdf_service import PDFService
from backend.services.file_service import FileService
from backend.services.notification_service import NotificationService
from backend.utils.logger import logger
from backend.utils.i18n_utils import get_translated_string

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
def predict_crop_task(self, n, p, k, temperature, humidity, ph, rainfall, user_id=None, lang='en'):
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
                title=get_translated_string("crop_prediction_ready_title", lang=lang),
                message=get_translated_string("crop_prediction_ready_msg", lang=lang, crop=crop),
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
def process_loan_task(self, json_data, user_id=None, lang='en'):
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
IMPORTANT: You MUST respond in the following language: {lang}. 
If the language code is 'hi', respond in Hindi. If 'mr', respond in Marathi. Default is English.
"""
        
        response = model.generate_content(prompt)
        
        if not response.candidates:
            return {'status': 'error', 'message': 'No response generated from Gemini API'}
        
        reply = response.candidates[0].content.parts[0].text
        
        # Trigger PDF Synthesis Task
        synthesize_loan_pdf_task.delay(json_data, reply, user_id, lang=lang)
        
        if user_id:
            NotificationService.create_notification(
                title=get_translated_string("loan_analysis_complete_title", lang=lang),
                message=get_translated_string("loan_analysis_complete_msg", lang=lang),
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
def synthesize_loan_pdf_task(self, user_data, analysis_result, user_id=None, lang='en'):
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
                title=get_translated_string("pdf_report_ready_title", lang=lang),
                message=get_translated_string("pdf_report_ready_msg", lang=lang, filename=file_record.original_name),
                notification_type="loan_update",
                user_id=user_id
            )
            
        return {'status': 'success', 'file_id': file_record.id}
    except Exception as e:
        logger.error(f"Async PDF synthesis failed: {str(e)}")
        if user_id:
            NotificationService.create_notification(
                title=get_translated_string("report_generation_failed_title", lang=lang),
                message=get_translated_string("report_generation_failed_msg", lang=lang),
                notification_type="system",
                user_id=user_id
            )
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.finalize_pool_cycle')
def finalize_pool_cycle_task(self, pool_id):
    """
    Finalize a completed pool cycle: execute profit distribution and
    transition to DISTRIBUTED state.
    """
    try:
        from backend.services.financial_service import FinancialService
        from backend.services.pool_service import PoolService
        from backend.models import YieldPool
        
        logger.info(f"Finalizing pool cycle for pool ID: {pool_id}")
        
        pool = YieldPool.query.get(pool_id)
        if not pool:
            return {'status': 'error', 'message': 'Pool not found'}
        
        if pool.status != 'COMPLETED':
            return {'status': 'error', 'message': f'Pool must be in COMPLETED state, currently {pool.status}'}
        
        # Execute profit distribution
        success, message = FinancialService.execute_distribution(pool_id)
        
        if not success:
            return {'status': 'error', 'message': message}
        
        # Transition to DISTRIBUTED state
        success, error = PoolService.transition_state(pool_id, 'DISTRIBUTED')
        
        if not success:
            return {'status': 'error', 'message': error}
        
        logger.info(f"Pool {pool.pool_id} finalized successfully")
        
        return {
            'status': 'success',
            'pool_id': pool.pool_id,
            'message': message
        }
        
    except Exception as e:
        logger.error(f"Failed to finalize pool cycle: {str(e)}")
        return {'status': 'error', 'message': str(e)}

CLAIM DETAILS:
- Claim Number: {claim.claim_number}
- Claimed Amount: ₹{claim.claimed_amount}
- Incident Date: {claim.incident_date}
- Incident Description: {claim.incident_description}

@celery_app.task(bind=True, name='tasks.simulate_batch_payouts')
def simulate_batch_payouts_task(self, pool_id):
    """
    Simulate bank transfers for all pool contributors.
    """
    try:
        from backend.services.financial_service import FinancialService
        from backend.models import YieldPool, PoolContribution
        
        logger.info(f"Simulating batch payouts for pool ID: {pool_id}")
        
        pool = YieldPool.query.get(pool_id)
        if not pool:
            return {'status': 'error', 'message': 'Pool not found'}
        
        contributions = PoolContribution.query.filter_by(pool_id=pool_id).all()
        
        results = []
        successful = 0
        failed = 0
        
        for contribution in contributions:
            if contribution.payout_status == 'PENDING' and contribution.actual_payout:
                result = FinancialService.simulate_bank_transfer(contribution.id)
                results.append({
                    'user_id': contribution.user_id,
                    'amount': contribution.actual_payout,
                    'result': result
                })
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
        
        logger.info(f"Batch payouts complete for pool {pool.pool_id}: {successful} successful, {failed} failed")
        
        return {
            'status': 'success',
            'pool_id': pool.pool_id,
            'successful_transfers': successful,
            'failed_transfers': failed,
            'details': results
        }
        
    except Exception as e:
        logger.error(f"Failed to simulate batch payouts: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.check_pool_target_reached')
def check_pool_target_reached_task(self):
    """
    Periodic task to check if any open pools have reached their target quantity
    and automatically transition them to LOCKED state.
    """
    try:
        from backend.services.pool_service import PoolService
        from backend.models import YieldPool
        
        # Find all open pools that have reached 100% of target
        pools = YieldPool.query.filter_by(status='OPEN').all()
        
        locked_count = 0
        
        for pool in pools:
            if pool.current_quantity >= pool.target_quantity:
                success, error = PoolService.transition_state(pool.id, 'LOCKED')
                
                if success:
                    locked_count += 1
                    logger.info(f"Auto-locked pool {pool.pool_id}: target reached")
        
        return {
            'status': 'success',
            'pools_locked': locked_count
        }
        
    except Exception as e:
        logger.error(f"Failed to check pool targets: {str(e)}")
        return {'status': 'error', 'message': str(e)}

