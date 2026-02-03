from backend.celery_app import celery_app
from backend.services.pdf_service import PDFService
from backend.services.traceability_service import TraceabilityService
from backend.services.file_service import FileService
from backend.services.notification_service import NotificationService
from backend.utils.i18n_utils import get_translated_string
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.generate_batch_certificate')
def generate_batch_certificate_task(self, batch_id, user_id=None, lang='en'):
    """
    Background task to generate a high-resolution quality certificate PDF for a batch.
    """
    try:
        logger.info(f"Starting certificate generation for batch: {batch_id}")
        
        # 1. Fetch full batch data including audit trail
        batch_data, error = TraceabilityService.get_batch_history(batch_id)
        if error:
            raise Exception(f"Failed to fetch batch data: {error}")
            
        # 2. Create temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
            
        # 3. Generate PDF
        success = PDFService.generate_traceability_certificate(batch_data, tmp_path)
        if not success:
            raise Exception("PDF certificate generation failed")
            
        # 4. Save to storage via FileService
        with open(tmp_path, 'rb') as f:
            class MockFile:
                def __init__(self, stream, filename):
                    self.stream = stream
                    self.filename = filename
                    self.content_type = 'application/pdf'
                def save(self, path):
                    with open(path, 'wb') as dest:
                        dest.write(self.stream.read())
                def seek(self, *args): self.stream.seek(*args)
                def tell(self): return self.stream.tell()
                
            mock_file = MockFile(f, f"Certificate_{batch_id}.pdf")
            file_record, fs_error = FileService.save_file(mock_file, user_id=user_id)
            if fs_error:
                raise Exception(f"File storage failed: {fs_error}")
                
        # 5. Clean up temp
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
        # 6. Update batch with certificate URL (simulated)
        # In a real app, you'd update SupplyBatch.certificate_url here
        
        # 7. Notify User
        if user_id:
            NotificationService.create_notification(
                title=get_translated_string("certificate_ready_title", lang=lang),
                message=get_translated_string("certificate_ready_msg", lang=lang, batch_id=batch_id),
                notification_type="system",
                user_id=user_id
            )
            
        return {'status': 'success', 'file_id': file_record.id, 'batch_id': batch_id}
        
    except Exception as e:
        logger.error(f"Certificate generation failed: {str(e)}")
        if user_id:
            NotificationService.create_notification(
                title="Certificate Generation Failed",
                message=f"Could not generate certificate for {batch_id}",
                notification_type="error",
                user_id=user_id
            )
        return {'status': 'error', 'message': str(e)}
