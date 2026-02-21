from datetime import datetime
from backend.extensions import db

class MigrationVector(db.Model):
    """
    Represents the predicted path of a pest or disease outbreak.
    """
    __tablename__ = 'migration_vectors'
    
    id = db.Column(db.Integer, primary_key=True)
    outbreak_zone_id = db.Column(db.Integer, db.ForeignKey('outbreak_zones.id'), nullable=False)
    
    # Vector Geometry
    origin_lat = db.Column(db.Float, nullable=False)
    origin_lng = db.Column(db.Float, nullable=False)
    target_lat = db.Column(db.Float, nullable=False)
    target_lng = db.Column(db.Float, nullable=False)
    
    # Dynamics (L3-1596)
    direction_degrees = db.Column(db.Float)
    speed_km_per_day = db.Column(db.Float)
    intensity_index = db.Column(db.Float) # 0.0 - 1.0 (Density of vectors)
    
    # Environmental Correlation
    wind_influence_factor = db.Column(db.Float)
    humidity_breeding_coeff = db.Column(db.Float)
    
    predicted_arrival_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContainmentZone(db.Model):
    """
    Bio-Security Blockade Zones.
    Enforces virtual and physical restrictions.
    """
    __tablename__ = 'containment_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_name = db.Column(db.String(100), nullable=False)
    
    # Geographic Boundary (Simplified as Circle for now)
    center_lat = db.Column(db.Float, nullable=False)
    center_lng = db.Column(db.Float, nullable=False)
    radius_meters = db.Column(db.Float, nullable=False)
    
    # Enforcement Levels: MONITORING, ADVISORY, RESTRICTED, LOCKED
    enforcement_level = db.Column(db.String(20), default='MONITORING')
    
    # Autonomous Flags
    irrigation_shutdown_triggered = db.Column(db.Boolean, default=False)
    logistics_blockade_active = db.Column(db.Boolean, default=False)
    
    quarantine_start = db.Column(db.DateTime, default=datetime.utcnow)
    quarantine_end = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.zone_name,
            'center': [self.center_lat, self.center_lng],
            'radius': self.radius_meters,
            'level': self.enforcement_level,
            'is_locked': self.logistics_blockade_active
        }
