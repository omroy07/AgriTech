from datetime import datetime, timedelta
from typing import Dict, Any
from backend.extensions import db
import json

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(100), nullable=True)
    resource_id = db.Column(db.String(100), nullable=True)
    
    # Details of the change
    old_values = db.Column(db.Text, nullable=True)  # JSON string
    new_values = db.Column(db.Text, nullable=True)  # JSON string
    
    # Request Info
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    method = db.Column(db.String(10), nullable=True)
    url = db.Column(db.String(1024), nullable=True)
    status_code = db.Column(db.Integer, nullable=True)
    
    # Risk Assessment
    risk_level = db.Column(db.String(20), default='LOW')  # LOW, MEDIUM, HIGH, CRITICAL
    threat_flag = db.Column(db.Boolean, default=False)
    
    # Financial Integrity (L3-1557 & L3-1560)
    is_financial = db.Column(db.Boolean, default=False)
    financial_impact = db.Column(db.Float, default=0.0)
    autonomous_decision_flag = db.Column(db.Boolean, default=False) # For AI-driven bidding
    
    # Smart Freight (L3-1631)
    ai_logistics_flag = db.Column(db.Boolean, default=False) # For geo-fence & phyto auto-decisions
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Meta data for extra context
    meta_data = db.Column(db.Text, nullable=True) # JSON string

    @property
    def gravity_score(self) -> int:
        """Calculates numerical significance for visualization."""
        base = {'CRITICAL': 100, 'HIGH': 75, 'MEDIUM': 50, 'LOW': 25}
        score = base.get(self.risk_level, 50)
        if self.threat_flag: score += 50
        return score

    @property
    def value_diff(self) -> Dict[str, Any]:
        """Calculates the difference between old and new values."""
        try:
            old = json.loads(self.old_values) if self.old_values else {}
            new = json.loads(self.new_values) if self.new_values else {}
            
            diff = {}
            # Simplified diff logic
            for key in new:
                if key not in old or old[key] != new[key]:
                    diff[key] = {"from": old.get(key), "to": new[key]}
            return diff
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': json.loads(self.old_values) if self.old_values else None,
            'new_values': json.loads(self.new_values) if self.new_values else None,
            'diff': self.value_diff,
            'ip_address': self.ip_address,
            'method': self.method,
            'url': self.url,
            'status_code': self.status_code,
            'risk_level': self.risk_level,
            'gravity': self.gravity_score,
            'threat_flag': self.threat_flag,
            'timestamp': self.timestamp.isoformat(),
            'meta_data': json.loads(self.meta_data) if self.meta_data else {}
        }

    @classmethod
    def archive_old_logs(cls, days: int = 90):
        """Prunes historical audit data to manage table size."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = cls.query.filter(cls.timestamp < cutoff).delete()
        db.session.commit()
        return deleted

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'login_time': self.login_time.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_active': self.is_active,
            'ip_address': self.ip_address
        }
