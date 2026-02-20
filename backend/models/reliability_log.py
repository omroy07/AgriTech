from datetime import datetime
from backend.extensions import db

class ReliabilityLog(db.Model):
    __tablename__ = 'reliability_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Snapshot of metrics at log time
    vibration_peak = db.Column(db.Float)
    temp_peak = db.Column(db.Float)
    oil_pressure = db.Column(db.Float)
    
    calculated_reliability_score = db.Column(db.Float) # The result of the update
    
    trigger_event = db.Column(db.String(50)) # "BOOKING_END", "DAILY_AUDIT", "MANUAL"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.recorded_at.isoformat(),
            'reliability_score': self.calculated_reliability_score,
            'trigger': self.trigger_event
        }
