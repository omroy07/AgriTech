from datetime import datetime
from backend.extensions import db
import json

class BarterStatus:
    PROPOSED = 'PROPOSED'
    ACCEPTED = 'ACCEPTED'
    ESCROW_LOCKED = 'ESCROW_LOCKED' # Both parties have "committed" their resources
    FULFILLED = 'FULFILLED' # Physical/Task exchange confirmed
    COMPLETED = 'COMPLETED' # Finalized, reputation updated
    CANCELLED = 'CANCELLED'

class BarterTransaction(db.Model):
    __tablename__ = 'barter_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    status = db.Column(db.String(20), default=BarterStatus.PROPOSED)
    
    # Dual-Lock Escrow State
    initiator_committed = db.Column(db.Boolean, default=False)
    responder_committed = db.Column(db.Boolean, default=False)
    
    # Verification of fulfillment
    initiator_confirmed_fulfillment = db.Column(db.Boolean, default=False)
    responder_confirmed_fulfillment = db.Column(db.Boolean, default=False)
    
    # Value Snapshot (JSON capturing the rates used for this trade)
    value_index_context = db.Column(db.Text) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resources = db.relationship('BarterResource', backref='transaction', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'initiator_id': self.initiator_id,
            'responder_id': self.responder_id,
            'status': self.status,
            'escrow': {
                'initiator_locked': self.initiator_committed,
                'responder_locked': self.responder_committed
            },
            'fulfillment': {
                'initiator_confirmed': self.initiator_confirmed_fulfillment,
                'responder_confirmed': self.responder_confirmed_fulfillment
            },
            'resources': [r.to_dict() for r in self.resources.all()],
            'created_at': self.created_at.isoformat()
        }

class BarterResource(db.Model):
    __tablename__ = 'barter_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('barter_transactions.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Resource Metadata
    resource_category = db.Column(db.String(50), nullable=False) # MACHINERY, LABOR, COMMODITY, SEEDS, CIRCULAR_CREDIT, WATER_QUOTA, CARBON_CREDIT
    resource_reference_id = db.Column(db.Integer) # e.g. Equipment ID, CircularCredit ID, CarbonMintEvent ID
    resource_name = db.Column(db.String(100))
    
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20)) # hours, kg, units
    
    # Value calculation at time of barter
    unit_value_index = db.Column(db.Float, nullable=False) # Value per unit
    total_value_index = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'category': self.resource_category,
            'ref_id': self.resource_reference_id,
            'name': self.resource_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'unit_value': self.unit_value_index,
            'total_value': self.total_value_index
        }

class ResourceValueIndex(db.Model):
    """Historical log of resource values for the Value-Index algorithm."""
    __tablename__ = 'resource_value_indices'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    item_name = db.Column(db.String(100), index=True)
    
    current_value = db.Column(db.Float, nullable=False)
    demand_multiplier = db.Column(db.Float, default=1.0)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
