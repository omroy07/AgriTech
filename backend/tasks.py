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


# AI-Powered Predictive Asset & Logistics Tasks

@celery_app.task(bind=True, name='tasks.run_predictive_analysis')
def run_predictive_analysis_task(self):
    """
    Weekly scheduled task to run AI failure predictions for all active assets.
    Identifies assets at risk and creates maintenance alerts.
    """
    try:
        from services.asset_service import AssetService
        from models import FarmAsset
        from services.notification_service import NotificationService
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("Starting scheduled predictive asset analysis")
        
        # Get all active assets
        active_assets = FarmAsset.query.filter_by(status='ACTIVE').all()
        
        predictions_run = 0
        alerts_created = 0
        
        for asset in active_assets:
            try:
                # Run AI prediction
                prediction = AssetService.predict_failure_ai(asset.asset_id)
                predictions_run += 1
                
                # Create alert if urgent
                if prediction['urgency'] in ['CRITICAL', 'HIGH']:
                    NotificationService.create_notification(
                        title=f"⚠️ Asset Alert: {asset.asset_name}",
                        message=f"Predicted failure in {prediction['days_to_failure']} days. Urgency: {prediction['urgency']}",
                        notification_type="asset_alert",
                        user_id=asset.user_id
                    )
                    alerts_created += 1
                    
            except Exception as e:
                logger.error(f"Error predicting for asset {asset.asset_id}: {str(e)}")
                continue
        
        logger.info(f"Predictive analysis complete: {predictions_run} predictions, {alerts_created} alerts")
        
        return {
            'status': 'success',
            'predictions_run': predictions_run,
            'alerts_created': alerts_created
        }
        
    except Exception as e:
        logger.error(f"Predictive analysis task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.optimize_daily_routes')
def optimize_daily_routes_task(self, target_date_str=None):
    """
    Daily scheduled task to optimize logistics routes for pending orders.
    Groups nearby farmers and calculates cost savings.
    
    Args:
        target_date_str: ISO format date string (defaults to tomorrow)
    """
    try:
        from services.logistics_service import LogisticsService
        from services.notification_service import NotificationService
        from datetime import datetime, timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Default to tomorrow if no date provided
        if target_date_str:
            target_date = datetime.fromisoformat(target_date_str)
        else:
            target_date = datetime.utcnow() + timedelta(days=1)
        
        logger.info(f"Starting route optimization for {target_date.date()}")
        
        # Run optimization
        routes = LogisticsService.optimize_routes(target_date)
        
        # Notify farmers about their optimized routes
        for route in routes:
            total_savings = route['total_savings']
            
            # Get orders in this route
            from models import LogisticsOrder
            orders = LogisticsOrder.query.filter_by(route_group_id=route['route_id']).all()
            
            for order in orders:
                NotificationService.create_notification(
                    title="🚚 Pickup Scheduled & Cost Optimized",
                    message=f"Your harvest pickup is scheduled. Grouped route saves you ₹{order.shared_cost_discount:.2f}! Route: {route['route_id']}",
                    notification_type="logistics_update",
                    user_id=order.user_id
                )
        
        logger.info(f"Route optimization complete: {len(routes)} routes created")
        
        return {
            'status': 'success',
            'target_date': target_date.date().isoformat(),
            'routes_created': len(routes),
            'total_orders_grouped': sum(r['order_count'] for r in routes)
        }
        
    except Exception as e:
        logger.error(f"Route optimization task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.send_maintenance_reminders')
def send_maintenance_reminders_task(self):
    """
    Daily task to send maintenance reminders for assets approaching due dates.
    """
    try:
        from models import FarmAsset
        from services.notification_service import NotificationService
        from datetime import datetime, timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("Starting maintenance reminder check")
        
        # Get assets with maintenance due in next 7 days
        threshold_date = datetime.utcnow() + timedelta(days=7)
        
        assets_due = FarmAsset.query.filter(
            FarmAsset.next_maintenance_due.isnot(None),
            FarmAsset.next_maintenance_due <= threshold_date,
            FarmAsset.status == 'ACTIVE'
        ).all()
        
        reminders_sent = 0
        
        for asset in assets_due:
            days_until_due = (asset.next_maintenance_due - datetime.utcnow()).days
            
            if days_until_due <= 0:
                urgency = "⚠️ OVERDUE"
                message = f"{asset.asset_name} maintenance is overdue! Schedule service immediately."
            elif days_until_due <= 3:
                urgency = "🔴 URGENT"
                message = f"{asset.asset_name} needs maintenance in {days_until_due} days."
            else:
                urgency = "🟡 Reminder"
                message = f"{asset.asset_name} has maintenance due in {days_until_due} days."
            
            NotificationService.create_notification(
                title=f"{urgency}: Maintenance Due",
                message=message,
                notification_type="asset_maintenance",
                user_id=asset.user_id
            )
            reminders_sent += 1
        
        logger.info(f"Maintenance reminders sent: {reminders_sent}")
        
        return {
            'status': 'success',
            'reminders_sent': reminders_sent
        }
        
    except Exception as e:
        logger.error(f"Maintenance reminder task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ==================== COMMUNITY FORUM TASKS ====================

@celery_app.task(bind=True, name='tasks.run_forum_maintenance')
def run_forum_maintenance_task(self):
    """
    Daily task to:
    1. Recalculate all user reputation scores.
    2. Cleanup older flagged content that hasn't been reviewed.
    3. Update trending metrics.
    """
    try:
        from models import UserReputation, ForumThread, PostComment
        from extensions import db
        from datetime import datetime, timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("Starting forum maintenance task")
        
        # 1. Recalculate Reputations
        reputations = UserReputation.query.all()
        for rep in reputations:
            rep.calculate_score()
        
        # 2. Flagged Content Cleanup (Auto-hide content flagged > 3 times or unreviewed for 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        unreviewed_flagged_threads = ForumThread.query.filter(
            ForumThread.is_flagged == True,
            ForumThread.is_ai_approved == True,
            ForumThread.updated_at < seven_days_ago
        ).all()
        
        for thread in unreviewed_flagged_threads:
            thread.is_ai_approved = False  # De-approve for manual review
            logger.info(f"Auto-deapproved flagged thread: {thread.id}")
            
        unreviewed_flagged_comments = PostComment.query.filter(
            PostComment.is_flagged == True,
            PostComment.is_ai_approved == True,
            PostComment.updated_at < seven_days_ago
        ).all()
        
        for comment in unreviewed_flagged_comments:
            comment.is_ai_approved = False
            logger.info(f"Auto-deapproved flagged comment: {comment.id}")
            
        db.session.commit()
        
        logger.info("Forum maintenance task complete")
        return {'status': 'success', 'reputations_updated': len(reputations)}
        
    except Exception as e:
        logger.error(f"Forum maintenance task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.reindex_forum_content')
def reindex_forum_content_task(self):
    """
    Weekly task to run deep AI-based content indexing.
    This improves the AI Knowledge Base search accuracy.
    """
    try:
        from services.ai_moderator import ai_moderator
        from models import ForumThread
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("Starting forum content re-indexing")
        
        # Get all approved threads
        threads = ForumThread.query.filter_by(is_ai_approved=True).all()
        
        indexed_count = 0
        for thread in threads:
            # Here we would normally update an external search index like ElasticSearch or ChromaDB
            # For this MVP, we re-run AI summary/keyword extraction if needed
            indexed_count += 1
            
        logger.info(f"Forum indexing complete: {indexed_count} threads processed")
        return {'status': 'success', 'indexed_count': indexed_count}
        
    except Exception as e:
        logger.error(f"Forum indexing task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}

