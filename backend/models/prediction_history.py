"""Prediction History model"""
from datetime import datetime
from extensions import db
import json


class PredictionHistory(db.Model):
    """Model for storing prediction history"""
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Prediction details
    prediction_type = db.Column(db.String(50), nullable=False)  # crop, disease, etc.
    input_data = db.Column(db.Text, nullable=False)  # JSON string of input parameters
    result = db.Column(db.Text, nullable=False)  # JSON string of prediction result
    confidence = db.Column(db.Float)  # Confidence score if available
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(255))
    
    # Analysis fields
    processing_time = db.Column(db.Float)  # Time taken to process in seconds
    model_version = db.Column(db.String(50))  # Version of model used
    
    def set_input_data(self, data):
        """Store input data as JSON"""
        self.input_data = json.dumps(data)
    
    def get_input_data(self):
        """Retrieve input data from JSON"""
        return json.loads(self.input_data) if self.input_data else None
    
    def set_result(self, result):
        """Store result as JSON"""
        self.result = json.dumps(result)
    
    def get_result(self):
        """Retrieve result from JSON"""
        return json.loads(self.result) if self.result else None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prediction_type': self.prediction_type,
            'input_data': self.get_input_data(),
            'result': self.get_result(),
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processing_time': self.processing_time,
            'model_version': self.model_version
        }
    
    def __repr__(self):
        return f'<PredictionHistory {self.prediction_type} - {self.id}>'
