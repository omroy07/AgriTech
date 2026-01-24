import os
import uuid
import magic
import boto3
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from backend.extensions import db
from backend.models import File
from backend.utils.logger import logger

class FileService:
    @staticmethod
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_type(file_stream):
        """Detect file type using magic numbers."""
        mime = magic.Magic(mime=True)
        file_stream.seek(0)
        file_type = mime.from_buffer(file_stream.read(2048))
        file_stream.seek(0)
        return file_type

    @staticmethod
    def save_file(file, user_id=None):
        """Save file to the configured storage backend."""
        if not file or not FileService.allowed_file(file.filename):
            return None, "Invalid file type"

        original_name = secure_filename(file.filename)
        extension = original_name.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        file_type = FileService.get_file_type(file.stream)
        file_size = 0 # Will be updated after save
        
        storage_type = current_app.config.get('STORAGE_TYPE', 'local')
        
        try:
            if storage_type == 's3':
                file_path = FileService._save_to_s3(file, unique_filename)
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
            else:
                file_path, file_size = FileService._save_to_local(file, unique_filename)

            # Create DB record
            new_file = File(
                user_id=user_id,
                filename=unique_filename,
                original_name=original_name,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                storage_type=storage_type
            )
            db.session.add(new_file)
            db.session.commit()

            # Generate thumbnail if it's an image
            if file_type.startswith('image/'):
                FileService.generate_thumbnail(file_path, storage_type)

            return new_file, None
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return None, str(e)

    @staticmethod
    def _save_to_local(file, filename):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, filename)
        file.seek(0)
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        return file_path, file_size

    @staticmethod
    def _save_to_s3(file, filename):
        s3 = boto3.client(
            's3',
            aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
            region_name=current_app.config['S3_REGION'],
            endpoint_url=current_app.config.get('S3_ENDPOINT_URL')
        )
        
        s3.upload_fileobj(
            file,
            current_app.config['S3_BUCKET'],
            filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        return filename # The S3 key

    @staticmethod
    def generate_thumbnail(file_path, storage_type):
        """Generate a small thumbnail for images."""
        try:
            if storage_type == 'local':
                with Image.open(file_path) as img:
                    img.thumbnail((200, 200))
                    thumb_path = f"{file_path}_thumb.jpg"
                    img.convert('RGB').save(thumb_path, "JPEG")
            # S3 thumbnail logic would involve downloading, processing, and re-uploading
        except Exception as e:
            logger.warning(f"Thumbnail generation failed: {str(e)}")

    @staticmethod
    def get_file_url(file_record):
        """Get a downloadable URL for the file."""
        if file_record.storage_type == 's3':
            s3 = boto3.client(
                's3',
                aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
                aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
                region_name=current_app.config['S3_REGION'],
                endpoint_url=current_app.config.get('S3_ENDPOINT_URL')
            )
            return s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': current_app.config['S3_BUCKET'], 'Key': file_record.file_path},
                ExpiresIn=3600
            )
        else:
            # For local files, we'd typically serve them via a specific route
            return f"/api/v1/files/download/{file_record.id}"
