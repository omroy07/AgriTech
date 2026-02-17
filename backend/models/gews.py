from datetime import datetime
from backend.extensions import db


class DiseaseIncident(db.Model):
    __tablename__ = 'disease_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disease_name = db.Column(db.String(100), nullable=False)
    crop_affected = db.Column(db.String(100), nullable=False)
    severity_level = db.Column(db.String(20), default='medium')
    symptoms = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    affected_area = db.Column(db.Float, default=0.0)
    detection_method = db.Column(db.String(50), default='manual')
    verification_status = db.Column(db.String(20), default='pending')
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    outbreak_zone_id = db.Column(db.Integer, db.ForeignKey('outbreak_zones.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'user_id': self.user_id,
            'disease_name': self.disease_name,
            'crop_affected': self.crop_affected,
            'severity_level': self.severity_level,
            'symptoms': self.symptoms,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'affected_area': self.affected_area,
            'detection_method': self.detection_method,
            'verification_status': self.verification_status,
            'reported_at': self.reported_at.isoformat() if self.reported_at else None
        }
    
    def to_geojson_feature(self):
        return {
            'type': 'Feature',
            'properties': self.to_dict(),
            'geometry': {
                'type': 'Point',
                'coordinates': [self.longitude, self.latitude]
            }
        }


class OutbreakZone(db.Model):
    __tablename__ = 'outbreak_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.String(50), unique=True, nullable=False)
    disease_name = db.Column(db.String(100), nullable=False)
    crop_affected = db.Column(db.String(100), nullable=False)
    severity_level = db.Column(db.String(20), default='medium')
    center_latitude = db.Column(db.Float, nullable=False)
    center_longitude = db.Column(db.Float, nullable=False)
    radius_km = db.Column(db.Float, nullable=False)
    incident_count = db.Column(db.Integer, default=0)
    total_affected_area = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')
    risk_level = db.Column(db.String(20), default='low')
    
    # Propagation Modelling
    propagation_velocity = db.Column(db.Float, default=0.0) # km/day
    transmission_radius = db.Column(db.Float, default=1.0) # km
    wind_vector_deg = db.Column(db.Float)
    soil_connectivity_score = db.Column(db.Float, default=0.5)
    
    # Autonomous Containment
    containment_status = db.Column(db.String(30), default='NONE') # NONE, IRRIGATION_LOCKDOWN, ACCESS_RESTRICTED, FULL_QUARANTINE
    containment_applied_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OutbreakProjection(db.Model):
    __tablename__ = 'outbreak_projections'
    
    id = db.Column(db.Integer, primary_key=True)
    outbreak_zone_id = db.Column(db.Integer, db.ForeignKey('outbreak_zones.id'), nullable=False)
    projection_time = db.Column(db.DateTime, nullable=False)
    
    projected_latitude = db.Column(db.Float, nullable=False)
    projected_longitude = db.Column(db.Float, nullable=False)
    expected_radius = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'outbreak_zone_id': self.outbreak_zone_id,
            'projection_time': self.projection_time.isoformat(),
            'latitude': self.projected_latitude,
            'longitude': self.projected_longitude,
            'radius': self.expected_radius,
            'confidence': self.confidence_score
        }

    def set_center_location(self, lat, lon):
        self.center_latitude = lat
        self.center_longitude = lon

    def to_dict(self):
        return {
            'id': self.id,
            'zone_id': self.zone_id,
            'disease_name': self.disease_name,
            'crop_affected': self.crop_affected,
            'severity_level': self.severity_level,
            'center_latitude': self.center_latitude,
            'center_longitude': self.center_longitude,
            'radius_km': self.radius_km,
            'incident_count': self.incident_count,
            'total_affected_area': self.total_affected_area,
            'status': self.status,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_geojson_feature(self):
        return {
            'type': 'Feature',
            'properties': self.to_dict(),
            'geometry': {
                'type': 'Point',
                'coordinates': [self.center_longitude, self.center_latitude]
            }
        }


class OutbreakAlert(db.Model):
    __tablename__ = 'outbreak_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey('outbreak_zones.id'), nullable=False)
    status = db.Column(db.String(20), default='active')
    priority = db.Column(db.String(20), default='medium')
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'user_id': self.user_id,
            'zone_id': self.zone_id,
            'status': self.status,
            'priority': self.priority,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }
