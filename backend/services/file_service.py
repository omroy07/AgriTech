import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.models import File

class FileService:
    @staticmethod
    def save_file(file, user_id=None):
        try:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file_path = os.path.join(upload_folder, unique_filename)
            
            # Reset stream pointer
            file.seek(0)
            file.save(file_path)
            
            file_record = File(
                user_id=user_id,
                filename=unique_filename,
                original_name=filename,
                file_path=file_path,
                file_type=file.content_type,
                mime_type=file.content_type,
                file_size=os.path.getsize(file_path),
                storage_type='local'
            )
            db.session.add(file_record)
            db.session.commit()
            
            return file_record, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
            
    @staticmethod
    def get_file_url(file_record):
        # Implementation depends on how files are served
        return f"/api/v1/files/download/{file_record.id}"
