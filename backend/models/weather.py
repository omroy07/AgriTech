from datetime import datetime
from backend.extensions import db

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False, index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall = db.Column(db.Float) # precipitation
    wind_speed = db.Column(db.Float)
    wind_direction = db.Column(db.Float) # degree, 0-360
    weather_condition = db.Column(db.String(50)) # e.g., 'Cloudy', 'Rainy'
    
    is_forecast = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'rainfall': self.rainfall,
            'wind_speed': self.wind_speed,
            'weather_condition': self.weather_condition,
            'timestamp': self.timestamp.isoformat()
        }

class CropAdvisory(db.Model):
    __tablename__ = 'crop_advisories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    
    advisory_text = db.Column(db.Text, nullable=False)
    growth_stage = db.Column(db.String(50)) # e.g., 'Seedling', 'Flowering'
    priority = db.Column(db.String(20), default='Normal') # 'Low', 'Normal', 'High', 'Emergency'
    
    # Context used for AI generation
    weather_summary = db.Column(db.Text)
    soil_summary = db.Column(db.Text)
    
    is_read = db.Column(db.Boolean, default=False)
    feedback_rating = db.Column(db.Integer) # 1-5
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_name': self.crop_name,
            'advisory_text': self.advisory_text,
            'growth_stage': self.growth_stage,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read
        }

class AdvisorySubscription(db.Model):
    __tablename__ = 'advisory_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    
    soil_type = db.Column(db.String(50))
    sowing_date = db.Column(db.Date)
    
    is_active = db.Column(db.Boolean, default=True)
    frequency = db.Column(db.String(20), default='Daily') # 'Daily', 'Weekly'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
