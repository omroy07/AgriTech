"""
Nutrient Optimization & Micronutrient Models — L3-1645
======================================================
Extends soil health monitoring to include micronutrient profiles and 
autonomous N-P-K-S balancing logs.
"""

from datetime import datetime
from backend.extensions import db

class FieldMicronutrients(db.Model):
    __tablename__ = 'field_micronutrients'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey('irrigation_zones.id'))
    
    # Micronutrient Ratios (ppm)
    zinc = db.Column(db.Float)
    iron = db.Column(db.Float)
    boron = db.Column(db.Float)
    manganese = db.Column(db.Float)
    copper = db.Column(db.Float)
    
    # Soil Activity Indices
    microbial_activity_index = db.Column(db.Float) # 0.0 to 5.0
    nutrient_availability_score = db.Column(db.Float) # Influence of pH
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class NutrientInjectionLog(db.Model):
    __tablename__ = 'nutrient_injection_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('irrigation_zones.id'), nullable=False)
    
    # N-P-K-S Mix composition
    nitrogen_content_pct = db.Column(db.Float)
    phosphorus_content_pct = db.Column(db.Float)
    potassium_content_pct = db.Column(db.Float)
    sulfur_content_pct = db.Column(db.Float)
    
    total_injected_volume_l = db.Column(db.Float)
    autonomous_trigger_code = db.Column(db.String(50)) # e.g., "LOW_NITROGEN_SPIKE"
    
    # Sustainability / Leaching metadata
    predicted_runoff_loss_pct = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'zone': self.zone_id,
            'npks': f"{self.nitrogen_content_pct}-{self.phosphorus_content_pct}-{self.potassium_content_pct}-{self.sulfur_content_pct}",
            'volume': self.total_injected_volume_l,
            'timestamp': self.recorded_at.isoformat()
        }
