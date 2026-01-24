from datetime import datetime
from backend.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    
    # Notification preferences
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    
    notifications = db.relationship('Notification', backref='user', lazy=True)
    files = db.relationship('File', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    websocket_sent = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'sent_at': self.sent_at.isoformat()
        }

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False) # Local path or S3 key
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False) # Size in bytes
    storage_type = db.Column(db.String(20), default='local') # 'local' or 's3'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'storage_type': self.storage_type,
            'created_at': self.created_at.isoformat()
        }
