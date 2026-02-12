from datetime import datetime
from backend.extensions import db
import json

class MediaPayload(db.Model):
    __tablename__ = 'media_payloads'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Payload identification
    tracking_id = db.Column(db.String(100), unique=True, nullable=False)
    payload_type = db.Column(db.String(50), nullable=False)  # DISEASE, SOIL, CROP, EQUIPMENT, PROFILE
    
    # File details
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    
    # Processing state
    status = db.Column(db.String(20), default='PENDING')  # PENDING, PROCESSING, COMPLETED, FAILED
    task_id = db.Column(db.String(100), nullable=True)  # Celery task ID
    
    # Extraction results
    processed_at = db.Column(db.DateTime, nullable=True)
    result_data = db.Column(db.Text, nullable=True)  # JSON string
    error_log = db.Column(db.Text, nullable=True)
    
    # Metadata context
    metadata_json = db.Column(db.Text, nullable=True)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tracking_id': self.tracking_id,
            'user_id': self.user_id,
            'payload_type': self.payload_type,
            'filename': self.filename,
            'status': self.status,
            'task_id': self.task_id,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'result': json.loads(self.result_data) if self.result_data else None,
            'metadata': json.loads(self.metadata_json) if self.metadata_json else {},
            'created_at': self.created_at.isoformat()
        }
