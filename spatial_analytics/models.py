from datetime import datetime
from backend.extensions import db

class Field(db.Model):
    __tablename__ = 'fields'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Store GeoJSON as text to ensure compatibility with SQLite and Postgres
    # Schema: { "type": "Feature", "geometry": { ... }, "properties": { ... } }
    boundary_geojson = db.Column(db.Text, nullable=False)
    
    area_hectares = db.Column(db.Float, nullable=True)
    crop_type = db.Column(db.String(50), nullable=True)
    sowing_date = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    analyses = db.relationship('FieldAnalysis', backref='field', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'boundary_geojson': self.boundary_geojson,
            'area_hectares': self.area_hectares,
            'crop_type': self.crop_type,
            'sowing_date': self.sowing_date.isoformat() if self.sowing_date else None,
            'created_at': self.created_at.isoformat()
        }

class FieldAnalysis(db.Model):
    __tablename__ = 'field_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)
    
    analysis_type = db.Column(db.String(50), nullable=False) # e.g., 'NDVI', 'SOIL_MOISTURE', 'DISEASE_RISK'
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Result values (e.g., {"mean_ndvi": 0.6, "health": "Good"})
    result_data = db.Column(db.JSON, nullable=True) 
    
    # Path to generated overlay image (relative to static/uploads)
    overlay_image_path = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'field_id': self.field_id,
            'analysis_type': self.analysis_type,
            'analysis_date': self.analysis_date.isoformat(),
            'result_data': self.result_data,
            'overlay_image_path': self.overlay_image_path
        }
