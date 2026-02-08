from datetime import datetime
from backend.extensions import db


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=False)
    storage_type = db.Column(db.String(20), default='local')
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

    def __repr__(self):
        return f'<File {self.id} - {self.original_name}>'


class YieldPool(db.Model):
    __tablename__ = 'yield_pools'
    
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.String(50), unique=True, nullable=False)
    pool_name = db.Column(db.String(200), nullable=False)
    crop_type = db.Column(db.String(100), nullable=False)
    target_quantity = db.Column(db.Float, nullable=False)
    current_quantity = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='OPEN', nullable=False)
    min_price_per_ton = db.Column(db.Float, nullable=False)
    current_offer_price = db.Column(db.Float, nullable=True)
    buyer_name = db.Column(db.String(200), nullable=True)
    collection_location = db.Column(db.String(200), nullable=False)
    logistics_overhead_percent = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    locked_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    distributed_at = db.Column(db.DateTime, nullable=True)
    
    contributions = db.relationship('PoolContribution', backref='pool', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('PoolVote', backref='pool', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'pool_name': self.pool_name,
            'crop_type': self.crop_type,
            'target_quantity': self.target_quantity,
            'current_quantity': self.current_quantity,
            'status': self.status,
            'min_price_per_ton': self.min_price_per_ton,
            'current_offer_price': self.current_offer_price,
            'buyer_name': self.buyer_name,
            'collection_location': self.collection_location,
            'logistics_overhead_percent': self.logistics_overhead_percent,
            'created_at': self.created_at.isoformat(),
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'distributed_at': self.distributed_at.isoformat() if self.distributed_at else None,
            'contribution_count': len(self.contributions),
            'fill_percentage': (self.current_quantity / self.target_quantity * 100) if self.target_quantity > 0 else 0
        }

    def get_risk_category(self):
        """Categorize risk score."""
        # Note: ars_score was probably intended to be risk_score or similar
        # Fallback to 50 if attribute missing
        score = getattr(self, 'ars_score', 50)
        if score <= 20: return 'EXCELLENT'
        elif score <= 40: return 'GOOD'
        elif score <= 60: return 'MODERATE'
        elif score <= 80: return 'HIGH'
        else: return 'CRITICAL'


class PoolContribution(db.Model):
    __tablename__ = 'pool_contributions'
    
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('yield_pools.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity_tons = db.Column(db.Float, nullable=False)
    quality_grade = db.Column(db.String(20), default='A')
    contribution_percentage = db.Column(db.Float, default=0.0)
    estimated_value = db.Column(db.Float, default=0.0)
    actual_payout = db.Column(db.Float, nullable=True)
    payout_status = db.Column(db.String(20), default='PENDING')
    contributed_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='pool_contributions')

    def to_dict(self):
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'quantity_tons': self.quantity_tons,
            'quality_grade': self.quality_grade,
            'contribution_percentage': self.contribution_percentage,
            'estimated_value': self.estimated_value,
            'actual_payout': self.actual_payout,
            'payout_status': self.payout_status,
            'contributed_at': self.contributed_at.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }


class ResourceShare(db.Model):
    __tablename__ = 'resource_shares'
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('yield_pools.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_type = db.Column(db.String(100), nullable=False)
    resource_name = db.Column(db.String(200), nullable=False)
    resource_value = db.Column(db.Float, nullable=False)
    usage_cost_per_hour = db.Column(db.Float, default=0.0)
    is_free_for_pool = db.Column(db.Boolean, default=True)
    availability_status = db.Column(db.String(20), default='AVAILABLE')
    shared_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    
    owner = db.relationship('User', backref='shared_resources')
    pool = db.relationship('YieldPool', backref='shared_resources')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'owner_id': self.owner_id,
            'owner_username': self.owner.username if self.owner else None,
            'resource_type': self.resource_type,
            'resource_name': self.resource_name,
            'resource_value': self.resource_value,
            'usage_cost_per_hour': self.usage_cost_per_hour,
            'is_free_for_pool': self.is_free_for_pool,
            'availability_status': self.availability_status,
            'shared_at': self.shared_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }


class PoolVote(db.Model):
    __tablename__ = 'pool_votes'
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('yield_pools.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vote = db.Column(db.String(10), nullable=False)
    offer_price = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='pool_votes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'vote': self.vote,
            'offer_price': self.offer_price,
            'comment': self.comment,
            'voted_at': self.voted_at.isoformat()
        }
