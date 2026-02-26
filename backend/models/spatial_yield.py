from datetime import datetime
from backend.extensions import db
from enum import Enum

class YieldPredictionConfidence(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    QUANTUM_CERTAINTY = "QUANTUM_CERTAINTY"

class SpatialYieldGrid(db.Model):
    __tablename__ = 'spatial_yield_grids'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.String(50), nullable=False, index=True) # GeoHash or H3 Index
    bounding_box_wkt = db.Column(db.Text, nullable=False)
    
    # Grid Environmental Variables
    avg_soil_moisture_pct = db.Column(db.Float)
    normalized_difference_vegetation_index = db.Column(db.Float) # NDVI
    canopy_temperature_c = db.Column(db.Float)
    
    # Aggregated Estimators
    projected_biomass_density = db.Column(db.Float)
    total_yield_potential_kg = db.Column(db.Float)
    
    last_satellite_pass = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'region_id': self.region_id,
            'ndvi': self.normalized_difference_vegetation_index,
            'yield_potential': self.total_yield_potential_kg,
            'last_sync': self.last_satellite_pass.isoformat() if self.last_satellite_pass else None
        }

class TemporalYieldForex(db.Model):
    __tablename__ = 'temporal_yield_forex'
    
    id = db.Column(db.Integer, primary_key=True)
    grid_id = db.Column(db.Integer, db.ForeignKey('spatial_yield_grids.id'), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)
    
    # Prophet Time Series Multipliers
    seasonality_vector = db.Column(db.JSON) # [jan_mult, feb_mult, ...]
    growth_acceleration_factor = db.Column(db.Float, default=1.0)
    
    base_yield_kg_per_hectare = db.Column(db.Float, nullable=False)
    predicted_harvest_date = db.Column(db.Date)
    
    confidence_level = db.Column(db.String(30), default=YieldPredictionConfidence.MEDIUM.value)
    
    engine_version = db.Column(db.String(20)) # e.g. "Prophet-v4.2"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_type': self.crop_type,
            'predicted_harvest': self.predicted_harvest_date.isoformat() if self.predicted_harvest_date else None,
            'base_yield': self.base_yield_kg_per_hectare,
            'confidence': self.confidence_level
        }
