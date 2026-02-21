from datetime import datetime
from backend.extensions import db

class SoilTest(db.Model):
    __tablename__ = 'soil_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    test_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    # Primary Nutrients (mg/kg or ppm)
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    
    # 3D Mapping / Nutrient Flux (L3-1547)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    depth_cm = db.Column(db.Float, default=15.0) # Sampling depth
    
    # Depth-based Ratios (Subsoil vs Topsoil)
    nitrogen_flux_index = db.Column(db.Float) 
    phosphorus_flux_index = db.Column(db.Float)
    leaching_susceptibility = db.Column(db.Float) # 0-1 score
    
    # Sustainability & Emissions (L3-1558)
    estimated_n2o_flux = db.Column(db.Float, default=0.0) # Emission factor based on N levels
    volatile_organic_compounds = db.Column(db.Float, default=0.0)
    
    # Soil Chemical Properties
    ph_level = db.Column(db.Float, nullable=False)
    organic_matter = db.Column(db.Float) # Percentage
    electrical_conductivity = db.Column(db.Float) # ds/m
    
    # Machinery Impact (L3-1603)
    soil_hardness_index = db.Column(db.Float, default=1.0) # Multiplier for component wear
    
    # Secondary Nutrients (ppm)
    calcium = db.Column(db.Float)
    magnesium = db.Column(db.Float)
    sulfur = db.Column(db.Float)
    
    lab_name = db.Column(db.String(150))
    report_url = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recommendations = db.relationship('FertilizerRecommendation', backref='soil_test', lazy='dynamic')
    application_logs = db.relationship('ApplicationLog', backref='soil_test', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'test_date': self.test_date.isoformat(),
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'ph_level': self.ph_level,
            'organic_matter': self.organic_matter,
            'ec': self.electrical_conductivity,
            'lab_name': self.lab_name,
            'created_at': self.created_at.isoformat()
        }

class FertilizerRecommendation(db.Model):
    __tablename__ = 'fertilizer_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    soil_test_id = db.Column(db.Integer, db.ForeignKey('soil_tests.id'), nullable=False)
    crop_type = db.Column(db.String(100), nullable=False)
    
    # Recommendations in kg/hectare
    rec_nitrogen = db.Column(db.Float)
    rec_phosphorus = db.Column(db.Float)
    rec_potassium = db.Column(db.Float)
    
    lime_requirement = db.Column(db.Float) # tons/hectare
    
    # Specific Fertilizer suggestions
    suggested_fertilizers = db.Column(db.Text) # JSON string: [{"name": "Urea", "amount": 100}, ...]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'soil_test_id': self.soil_test_id,
            'crop_type': self.crop_type,
            'nitrogen': self.rec_nitrogen,
            'phosphorus': self.rec_phosphorus,
            'potassium': self.rec_potassium,
            'lime': self.lime_requirement,
            'suggestions': json.loads(self.suggested_fertilizers) if self.suggested_fertilizers else [],
            'created_at': self.created_at.isoformat()
        }

class ApplicationLog(db.Model):
    __tablename__ = 'fertilizer_application_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    soil_test_id = db.Column(db.Integer, db.ForeignKey('soil_tests.id'), nullable=False)
    applied_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    fertilizer_name = db.Column(db.String(100), nullable=False)
    amount_applied = db.Column(db.Float, nullable=False) # kg
    area_covered = db.Column(db.Float, nullable=False) # Hectares
    
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
