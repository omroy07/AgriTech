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

class RiskTrigger(db.Model):
    __tablename__ = 'weather_risk_triggers'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_type = db.Column(db.String(100), nullable=False)
    
    # Thresholds
    max_temp_threshold = db.Column(db.Float)
    min_temp_threshold = db.Column(db.Float)
    max_rainfall_threshold = db.Column(db.Float) # mm
    max_wind_speed = db.Column(db.Float)
    
    severity_level = db.Column(db.String(20), default='WARNING') # WARNING, CRITICAL, EMERGENCY
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ClimateTelemetryEvent(db.Model):
    """
    Satellite / IoT weather telemetry stream (L3-1630).
    Each row = one sensor reading for a farm location.
    The Yield Resilience Engine scans this table to detect Force Majeure streaks.
    """
    __tablename__ = 'climate_telemetry_events'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    location = db.Column(db.String(150))

    # Core metrics
    temperature_c = db.Column(db.Float, nullable=False)
    rainfall_mm = db.Column(db.Float, default=0.0)
    humidity_pct = db.Column(db.Float)
    wind_speed_kmh = db.Column(db.Float)
    solar_radiation_wm2 = db.Column(db.Float)  # Watt per m² — heat stress proxy

    # Classification applied by the engine
    is_extreme = db.Column(db.Boolean, default=False)
    extreme_type = db.Column(db.String(50))  # HEAT_WAVE, FROST, CYCLONE, FLOOD, DROUGHT

    source = db.Column(db.String(50), default='IOT_SENSOR')  # IOT_SENSOR, SATELLITE
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'temperature_c': self.temperature_c,
            'rainfall_mm': self.rainfall_mm,
            'humidity_pct': self.humidity_pct,
            'is_extreme': self.is_extreme,
            'extreme_type': self.extreme_type,
            'recorded_at': self.recorded_at.isoformat()
        }

class ForceMajeureAlert(db.Model):
    """
    Raised when extreme climate events persist past the parametric trigger threshold
    (e.g., 3 consecutive days above 45°C). This record drives auto-settlement (L3-1630).
    """
    __tablename__ = 'force_majeure_alerts'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)

    # Trigger definition
    trigger_type = db.Column(db.String(50), nullable=False)   # HEAT_WAVE, FROST, FLOOD, DROUGHT
    threshold_value = db.Column(db.Float)                     # e.g., 45.0°C
    consecutive_days = db.Column(db.Integer, nullable=False)  # observed streak

    # Status: ACTIVE, AUTO_SETTLED, DISMISSED, EXPIRED
    status = db.Column(db.String(20), default='ACTIVE')

    # Auto-settlement linkage
    auto_settled = db.Column(db.Boolean, default=False)
    settlement_ledger_txn_id = db.Column(db.Integer, db.ForeignKey('ledger_transactions.id'))

    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'trigger_type': self.trigger_type,
            'threshold_value': self.threshold_value,
            'consecutive_days': self.consecutive_days,
            'status': self.status,
            'auto_settled': self.auto_settled,
            'triggered_at': self.triggered_at.isoformat()
        }

class ParametricPolicyTrigger(db.Model):
    """
    Maps a CropPolicy to its parametric climate triggers (L3-1630).
    Replaces subjective manual claims with objective data conditions.
    """
    __tablename__ = 'parametric_policy_triggers'

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('crop_policies.id'), nullable=False)

    trigger_type = db.Column(db.String(50), nullable=False)  # HEAT_WAVE, FROST, FLOOD
    threshold_value = db.Column(db.Float, nullable=False)    # e.g., 45°C, 0°C, 150mm
    required_consecutive_days = db.Column(db.Integer, default=3)

    # Payout percentage of coverage_amount when triggered
    payout_percentage = db.Column(db.Float, default=100.0)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'trigger_type': self.trigger_type,
            'threshold_value': self.threshold_value,
            'required_consecutive_days': self.required_consecutive_days,
            'payout_percentage': self.payout_percentage,
            'is_active': self.is_active
        }
