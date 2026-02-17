from datetime import datetime
from backend.extensions import db

class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for broadcast
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Priority: LOW, MEDIUM, HIGH, CRITICAL
    priority = db.Column(db.String(20), default='MEDIUM', nullable=False)
    
    # Category: WEATHER, MARKET, FORUM, SYSTEM, SECURITY, LOAN
    category = db.Column(db.String(50), nullable=False)
    
    # Grouping key for similar alerts
    group_key = db.Column(db.String(100), nullable=True)
    
    # Delivery Channels Status
    websocket_delivered = db.Column(db.Boolean, default=False)
    email_delivered = db.Column(db.Boolean, default=False)
    sms_delivered = db.Column(db.Boolean, default=False)
    push_delivered = db.Column(db.Boolean, default=False)
    
    # Expiry for cleanup
    expires_at = db.Column(db.DateTime, nullable=True)
    
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata for deep-linking
    action_url = db.Column(db.String(512), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)  # JSON string for extra data

    @property
    def gravity_score(self) -> int:
        """Calculates a numerical score for alert importance."""
        base_scores = {'CRITICAL': 100, 'HIGH': 75, 'MEDIUM': 50, 'LOW': 25}
        score = base_scores.get(self.priority, 50)
        
        # Boost score if category is high-risk
        if self.category in ['SECURITY', 'MARKET']:
            score += 20
        
        return score

    def validate(self):
        """Validates alert data before persistence."""
        if not self.title or len(self.title) < 5:
            raise ValueError("Alert title must be at least 5 characters long.")
        if not self.category:
            raise ValueError("Alert category is required.")
        if self.priority not in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            raise ValueError("Invalid priority level.")
        return True

    def to_dict(self):
        """Serializes alert data for API and WebSocket delivery."""
        res = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'category': self.category,
            'gravity': self.gravity_score,
            'group_key': self.group_key,
            'delivery_report': {
                'websocket': self.websocket_delivered,
                'email': self.email_delivered,
                'sms': self.sms_delivered,
                'push': self.push_delivered
            },
            'status': 'READ' if self.read_at else 'UNREAD',
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'action_url': self.action_url,
            'is_expired': self.expires_at < datetime.utcnow() if self.expires_at else False
        }
        
        # Parse metadata safely
        try:
            res['metadata'] = json.loads(self.metadata_json) if self.metadata_json else {}
        except Exception:
            res['metadata'] = {}
            
        return res

    @staticmethod
    def get_priority_weight(priority):
        """Helper to compare priority levels numerically."""
        weights = {'CRITICAL': 40, 'HIGH': 30, 'MEDIUM': 20, 'LOW': 10}
        return weights.get(priority, 0)

class AlertPreference(db.Model):
    __tablename__ = 'alert_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    push_enabled = db.Column(db.Boolean, default=True)
    websocket_enabled = db.Column(db.Boolean, default=True)
    
    min_priority = db.Column(db.String(20), default='LOW')

    def to_dict(self):
        return {
            'category': self.category,
            'email_enabled': self.email_enabled,
            'sms_enabled': self.sms_enabled,
            'push_enabled': self.push_enabled,
            'websocket_enabled': self.websocket_enabled,
            'min_priority': self.min_priority
        }
