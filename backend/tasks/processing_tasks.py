from backend.celery_app import celery_app
from backend.models.processing import ProcessingBatch, ProcessingStage
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.monitor_stale_batches')
def monitor_stale_batches_task():
    """Detect batches that have been stuck in a stage for more than 48 hours"""
    threshold = datetime.utcnow() - timedelta(hours=48)
    stale_batches = ProcessingBatch.query.filter(
        ProcessingBatch.current_stage != ProcessingStage.COMPLETED.value,
        ProcessingBatch.updated_at < threshold
    ).all()
    
    for batch in stale_batches:
        logger.warning(f"Production Lag: Batch {batch.batch_number} is stale in {batch.current_stage} stage.")
        
    return {'status': 'success', 'stale_count': len(stale_batches)}

@celery_app.task(name='tasks.daily_production_report')
def daily_production_report_task():
    """Aggregate stats for completed batches in the last 24h"""
    yesterday = datetime.utcnow() - timedelta(days=1)
    batch_count = ProcessingBatch.query.filter(
        ProcessingBatch.completed_at >= yesterday
    ).count()
    
    total_output = db.session.query(db.func.sum(ProcessingBatch.current_weight))\
        .filter(ProcessingBatch.completed_at >= yesterday).scalar() or 0
        
    logger.info(f"Daily Production: Generated {batch_count} batches with {total_output} kg total yield.")
    return {
        'batches_completed': batch_count,
        'total_kg': float(total_output)
    }

@celery_app.task(name='tasks.process_media_pipeline')
def process_media_pipeline(payload_id):
    """
    Unified dispatcher for background processing of images and data.
    UDEMP Pipeline Integration.
    """
    from backend.models.media_payload import MediaPayload
    from backend.services.pipeline_service import MediaPipelineService
    import time
    
    payload = MediaPayload.query.get(payload_id)
    if not payload:
        return {'status': 'error', 'message': 'Payload not found'}

    try:
        if payload.payload_type == 'DISEASE':
            result = _process_disease_image(payload)
        elif payload.payload_type == 'SOIL':
            result = _process_soil_data(payload)
        else:
            result = {'message': 'No specialized processor found for this type'}

        MediaPipelineService.attach_result(payload_id, result)
        return {'status': 'success', 'tracking_id': payload.tracking_id}
        
    except Exception as e:
        logger.error(f"Pipeline processing failed for {payload_id}: {str(e)}")
        from backend.services.pipeline_service import MediaPipelineService
        MediaPipelineService.attach_result(payload_id, {}, status='FAILED', error=str(e))
        return {'status': 'failed', 'error': str(e)}

def _process_disease_image(payload):
    """
    Integrates with the Disease Prediction module logic.
    Loads model dynamically to save memory on worker start.
    """
    import sys
    # Add external module path if not in PYTHONPATH
    module_path = os.path.join(os.getcwd(), 'Disease prediction')
    if module_path not in sys.path:
        sys.path.append(module_path)
        
    try:
        from utils import load_keras_model, predict_image_keras
        
        # Load model (caching strategy recommended in prod)
        model_path = os.path.join(module_path, 'model.h5')
        if not os.path.exists(model_path):
             # Fallback for dev environment without model file
             return {
                 'prediction': 'Simulation: Bacterial Blight',
                 'confidence': 0.95,
                 'recommendation': 'Mock: Apply Copper Fungicide',
                 'note': 'Real model not found at ' + model_path
             }
             
        model = load_keras_model(model_path)
        prediction, description = predict_image_keras(model, payload.file_path)
        
        return {
            'prediction': prediction,
            'confidence': 0.99, # Placeholder as utils doesn't return confidence
            'recommendation': description,
            'crop_context': 'Detected from Image'
        }
    except ImportError:
        return {'error': 'Disease prediction module unavailable'}
    except Exception as e:
        return {'error': f'Inference failed: {str(e)}'}

def _process_soil_data(payload):
    """
    Integrates with Soil Classification logic.
    """
    import sys
    # Add external module path
    module_path = os.path.join(os.getcwd(), 'Soil Classification Model')
    if module_path not in sys.path:
        sys.path.append(module_path)
        
    try:
        from main import SoilClassifier
        
        classifier = SoilClassifier()
        # For soil, we might process an image or CSV. 
        # Assuming payload.file_path points to the input.
        result = classifier.predict(payload.file_path)
        
        return result
    except ImportError:
        return {'error': 'Soil classification module unavailable'}
    except Exception as e:
        return {'error': f'Classification failed: {str(e)}'}
