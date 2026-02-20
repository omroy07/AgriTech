import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
from werkzeug.utils import secure_filename
from flask import current_app
from backend.extensions import db
from backend.models import MediaPayload
from backend.utils.validators import DataIntegrityValidator
from backend.utils.logger import logger

class MediaPipelineService:
    """
    Central logic for media ingestion, metadata mapping, and task dispatching.
    """

    @staticmethod
    def ingest_payload(
        file_obj,
        payload_type: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> (Optional[MediaPayload], Optional[str]):
        """
        Main entry point for uploading and starting the processing pipeline.
        """
        try:
            # 1. Setup Storage Path
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], payload_type.lower())
            os.makedirs(upload_dir, exist_ok=True)
            
            # 2. Secure Filename
            original_filename = secure_filename(file_obj.filename)
            tracking_id = str(uuid.uuid4())
            extension = os.path.splitext(original_filename)[1]
            stored_filename = f"{tracking_id}{extension}"
            file_path = os.path.join(upload_dir, stored_filename)
            
            # 3. Save to Disk temporarily for validation
            file_obj.save(file_path)
            
            # 4. Deep Validation
            is_valid, error = DataIntegrityValidator.validate_file(file_path, payload_type)
            if not is_valid:
                os.remove(file_path)
                return None, error
                
            is_meta_valid, meta_error = DataIntegrityValidator.validate_metadata(metadata or {}, payload_type)
            if not is_meta_valid:
                os.remove(file_path)
                return None, meta_error

            # 5. Create Registry Entry
            payload = MediaPayload(
                user_id=user_id,
                tracking_id=tracking_id,
                payload_type=payload_type,
                filename=original_filename,
                file_path=file_path,
                file_type=os.path.splitext(file_path)[1],
                file_size=os.path.getsize(file_path),
                metadata_json=json.dumps(metadata) if metadata else None
            )
            
            db.session.add(payload)
            db.session.commit()
            
            # 6. Dispatch Asynchronous Processing
            MediaPipelineService._dispatch_task(payload)
            
            return payload, None
        except Exception as e:
            logger.error(f"Media ingestion failed: {str(e)}", exc_info=True)
            return None, str(e)

    @staticmethod
    def _dispatch_task(payload: MediaPayload):
        """
        Triggers the appropriate Celery task based on payload type.
        """
        from backend.tasks.processing_tasks import process_media_pipeline
        task = process_media_pipeline.delay(payload.id)
        payload.task_id = task.id
        payload.status = 'PROCESSING'
        db.session.commit()

    @staticmethod
    def get_payload_status(tracking_id: str) -> Optional[MediaPayload]:
        return MediaPayload.query.filter_by(tracking_id=tracking_id).first()

    @staticmethod
    def attach_result(payload_id: int, result: Dict, status: str = 'COMPLETED', error: str = None):
        """
        Callback for tasks to update payload with findings.
        """
        payload = MediaPayload.query.get(payload_id)
        if payload:
            payload.result_data = json.dumps(result)
            payload.status = status
            payload.processed_at = datetime.utcnow()
            payload.error_log = error
            db.session.commit()
            
            # Trigger real-time update via SocketIO
            from backend.extensions import socketio
            socketio.emit('pipeline_update', payload.to_dict(), room=f"user_{payload.user_id}")
