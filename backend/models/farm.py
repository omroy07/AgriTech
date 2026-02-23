from datetime import datetime
from backend.extensions import db
from enum import Enum

class FarmRole(Enum):
    OWNER = "owner"
    MANAGER = "manager"
    WORKER = "worker"
    VIEWER = "viewer"

class Farm(db.Model):
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255), nullable=False)
    acreage = db.Column(db.Float)
    
    # Metadata as JSON
    soil_details = db.Column(db.Text) # e.g., {"type": "Loamy", "pH": 6.5}
    
    # Predictive Harvest Velocity (L3-1560)
    harvest_readiness_index = db.Column(db.Float, default=0.0) # 0-100%
    predicted_yield_volume = db.Column(db.Float, default=0.0) # Estimated kg
    last_velocity_update = db.Column(db.DateTime)
    
    # Regenerative Carbon Tracking (L3-1632)
    is_no_till = db.Column(db.Boolean, default=False)            # No-tillage practice
    cover_crop_active = db.Column(db.Boolean, default=False)      # Cover cropping in rotation
    organic_certified = db.Column(db.Boolean, default=False)      # Certified organic (no synthetic)
    sequestration_tier = db.Column(db.String(20), default='TIER_1') # TIER_1 to TIER_4
    total_carbon_credits_minted = db.Column(db.Float, default=0.0) # Lifetime credits earned
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('FarmMember', backref='farm', lazy='dynamic', cascade='all, delete-orphan')
    assets = db.relationship('FarmAsset', backref='farm', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'acreage': self.acreage,
            'soil_details': json.loads(self.soil_details) if self.soil_details else {},
            'member_count': self.members.count(),
            'created_at': self.created_at.isoformat()
        }

class FarmMember(db.Model):
    __tablename__ = 'farm_members'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    role = db.Column(db.String(20), default=FarmRole.WORKER.value)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Track who invited them
    invited_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat()
        }

class FarmAsset(db.Model):
    __tablename__ = 'farm_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., Tractor, Irrigation Pump, Storehouse
    purchase_value = db.Column(db.Float)
    purchase_date = db.Column(db.DateTime)
    
    condition = db.Column(db.String(50), default='Good') # 'Good', 'Needs Repair', 'Critical'
    last_maintenance = db.Column(db.DateTime)
    
    # Depreciated value tracker
    current_valuation = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'name': self.name,
            'category': self.category,
            'purchase_value': self.purchase_value,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'condition': self.condition,
            'current_valuation': self.current_valuation,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None
        }
