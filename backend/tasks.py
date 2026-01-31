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


@celery_app.task(bind=True, name='tasks.detect_disease_outbreaks')
def detect_disease_outbreaks_task(self):
    """
    Automated task to detect disease outbreaks by analyzing spatial clustering.
    Runs every hour to identify new outbreak zones and alert at-risk farmers.
    """
    try:
        from backend.services.geospatial_service import GeospatialService
        from backend.models import OutbreakZone
        from sqlalchemy import func, and_
        import uuid
        
        logger.info("Starting outbreak detection analysis...")
        
        # Detect outbreak clusters
        clusters = GeospatialService.detect_outbreak_clusters(
            radius_km=50,  # 50km clustering radius
            min_incidents=3,  # Minimum 3 incidents
            days_back=30  # Last 30 days
        )
        
        new_outbreaks = []
        
        for cluster in clusters:
            # Check if similar outbreak zone already exists
            existing_zone = OutbreakZone.query.filter(
                and_(
                    OutbreakZone.disease_name == cluster['disease_name'],
                    OutbreakZone.crop_affected == cluster['crop_affected'],
                    OutbreakZone.status == 'active',
                    func.abs(OutbreakZone.center_latitude - cluster['center_lat']) < 0.1,
                    func.abs(OutbreakZone.center_longitude - cluster['center_lon']) < 0.1
                )
            ).first()
            
            if existing_zone:
                # Update existing zone
                existing_zone.incident_count = cluster['incident_count']
                existing_zone.total_affected_area = cluster.get('total_affected_area', 0)
                existing_zone.severity_level = cluster['severity_level']
                existing_zone.last_updated = datetime.utcnow()
                logger.info(f"Updated existing outbreak zone: {existing_zone.zone_id}")
            else:
                # Create new outbreak zone
                zone = GeospatialService.create_outbreak_zone(cluster)
                new_outbreaks.append(zone)
                logger.info(f"Created new outbreak zone: {zone.zone_id}")
                
                # Trigger emergency alerts
                send_outbreak_emergency_alerts_task.delay(zone.id)
        
        db.session.commit()
        
        return {
            'status': 'success',
            'clusters_detected': len(clusters),
            'new_outbreaks': len(new_outbreaks),
            'new_outbreak_ids': [z.zone_id for z in new_outbreaks]
        }
    
    except Exception as e:
        logger.error(f"Outbreak detection failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.send_outbreak_emergency_alerts')
def send_outbreak_emergency_alerts_task(self, outbreak_zone_id):
    """
    Send emergency alerts and generate PDF reports for farmers at risk.
    """
    try:
        from backend.services.geospatial_service import GeospatialService
        from backend.services.notification_service import NotificationService
        from backend.models import OutbreakZone, OutbreakAlert
        from backend.extensions.socketio import socketio
        from sqlalchemy import and_
        import uuid
        
        zone = OutbreakZone.query.get(outbreak_zone_id)
        if not zone:
            return {'status': 'error', 'message': 'Outbreak zone not found'}
        
        # Find farmers at risk
        at_risk_farmers = GeospatialService.find_farmers_at_risk(zone, radius_multiplier=1.5)
        
        logger.info(f"Found {len(at_risk_farmers)} farmers at risk for outbreak {zone.zone_id}")
        
        alerts_sent = []
        
        for farmer, distance in at_risk_farmers:
            # Skip if already alerted for this zone
            existing_alert = OutbreakAlert.query.filter(
                and_(
                    OutbreakAlert.user_id == farmer.id,
                    OutbreakAlert.outbreak_zone_id == zone.id
                )
            ).first()
            
            if existing_alert:
                continue
            
            # Determine priority based on distance and risk level
            if distance <= zone.radius_km:
                priority = 'urgent'
                alert_type = 'outbreak_detected'
            elif distance <= zone.radius_km * 1.2:
                priority = 'high'
                alert_type = 'proximity_warning'
            else:
                priority = 'medium'
                alert_type = 'preventive_action'
            
            # Get localized messages
            lang = 'en'  # TODO: Get user's preferred language
            title = get_translated_string(f'outbreak_alert_{alert_type}_title', lang=lang,
                                         disease=zone.disease_name)
            message = get_translated_string(f'outbreak_alert_{alert_type}_msg', lang=lang,
                                           disease=zone.disease_name,
                                           crop=zone.crop_affected,
                                           distance=f"{distance:.1f}")
            
            # Create outbreak alert record
            alert_id = f"ALERT-{uuid.uuid4().hex[:12].upper()}"
            alert = OutbreakAlert(
                alert_id=alert_id,
                user_id=farmer.id,
                outbreak_zone_id=zone.id,
                alert_type=alert_type,
                priority=priority,
                title=title,
                message=message,
                distance_km=distance
            )
            
            db.session.add(alert)
            db.session.flush()
            
            # Send SocketIO real-time notification
            try:
                socketio.emit('outbreak_alert', {
                    'alert_id': alert_id,
                    'zone_id': zone.zone_id,
                    'title': title,
                    'message': message,
                    'priority': priority,
                    'distance_km': distance,
                    'disease_name': zone.disease_name,
                    'crop_affected': zone.crop_affected
                }, room=f'user_{farmer.id}')
            except Exception as e:
                logger.warning(f"SocketIO emit failed: {str(e)}")
            
            # Create regular notification
            NotificationService.create_notification(
                title=title,
                message=message,
                notification_type='outbreak_alert',
                user_id=farmer.id
            )
            
            # Generate PDF report asynchronously
            generate_outbreak_pdf_report_task.delay(alert.id, lang=lang)
            
            alerts_sent.append(alert_id)
        
        db.session.commit()
        
        return {
            'status': 'success',
            'alerts_sent': len(alerts_sent),
            'alert_ids': alerts_sent
        }
    
    except Exception as e:
        logger.error(f"Emergency alert sending failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.generate_outbreak_pdf_report')
def generate_outbreak_pdf_report_task(self, alert_id, lang='en'):
    """
    Generate AI-powered preventative action PDF report for outbreak alert.
    """
    try:
        import google.generativeai as genai
        from backend.services.pdf_service import PDFService
        from backend.services.file_service import FileService
        from backend.models import OutbreakAlert
        
        alert = OutbreakAlert.query.get(alert_id)
        if not alert or not alert.zone:
            return {'status': 'error', 'message': 'Alert or zone not found'}
        
        zone = alert.zone
        
        # Generate AI preventative measures if not already generated
        if not zone.preventative_measures or not zone.emergency_recommendations:
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                
                prompt = f"""
You are an agricultural disease management expert. Generate a comprehensive emergency response report.

OUTBREAK DETAILS:
- Disease: {zone.disease_name}
- Affected Crop: {zone.crop_affected}
- Severity Level: {zone.severity_level}
- Risk Level: {zone.risk_level}
- Number of Incidents: {zone.incident_count}
- Affected Area: {zone.total_affected_area} hectares

Generate a detailed report with:
1. IMMEDIATE ACTIONS (next 24-48 hours)
2. PREVENTATIVE MEASURES (to protect crops)
3. TREATMENT RECOMMENDATIONS (if infection occurs)
4. MONITORING GUIDELINES
5. COMMUNITY COORDINATION STEPS

Language: {lang}
Format: Use clear sections with bullet points. Be specific and actionable.
"""
                
                response = model.generate_content(prompt)
                if response.candidates:
                    recommendations = response.candidates[0].content.parts[0].text
                    zone.emergency_recommendations = recommendations
                    zone.preventative_measures = recommendations[:500]  # Store summary
                    db.session.commit()
        
        # Generate PDF report
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        
        pdf_data = {
            'zone': zone.to_dict(),
            'alert': alert.to_dict(),
            'distance_km': alert.distance_km,
            'recommendations': zone.emergency_recommendations or "Consult local agricultural expert."
        }
        
        # Use PDFService to generate report (simplified here)
        success = PDFService.generate_outbreak_report(pdf_data, tmp_path)
        
        if success:
            # Save PDF file
            with open(tmp_path, 'rb') as f:
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
                
                mock_file = MockFile(f, f"Outbreak_Alert_{zone.zone_id}_{datetime.now().strftime('%Y%m%d')}.pdf")
                file_record, error = FileService.save_file(mock_file, user_id=alert.user_id)
                
                if not error:
                    alert.pdf_report_id = file_record.id
                    db.session.commit()
        
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        
        return {'status': 'success', 'alert_id': alert_id}
    
    except Exception as e:
        logger.error(f"PDF report generation failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}
