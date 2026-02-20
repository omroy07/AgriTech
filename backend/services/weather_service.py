from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.weather import WeatherData, AdvisorySubscription
from backend.utils.weather_api_client import WeatherAPIClient
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    @staticmethod
    def update_weather_for_location(location):
        """Fetch latest weather and store in database"""
        client = WeatherAPIClient()
        raw_data = client.get_current_weather(location)
        
        if not raw_data:
            return None
            
        weather = WeatherData(
            location=location,
            temperature=raw_data['main']['temp'],
            humidity=raw_data['main']['humidity'],
            rainfall=raw_data.get('rain', {}).get('1h', 0) if 'rain' in raw_data else 0,
            wind_speed=raw_data['wind']['speed'],
            wind_direction=raw_data['wind'].get('deg', 0),
            weather_condition=raw_data['weather'][0]['main']
        )
        
        db.session.add(weather)
        db.session.commit()
        
        # Trigger Alerts for Extreme Conditions
        # Note: In a real app we'd query users in this location
        from backend.services.alert_registry import AlertRegistry
        
        if weather.temperature > 40:
            AlertRegistry.register_alert(
                title="Extreme Heat Alert",
                message=f"Location {location} is experiencing extreme heat ({weather.temperature}°C). Please protect your crops.",
                category="WEATHER",
                priority="HIGH",
                group_key=f"heat_{location}"
            )
            
        if weather.rainfall > 50:
             # Critical: Auto-Stop Fertigation
             from backend.services.fertigation_service import FertigationService
             from backend.models.irrigation import IrrigationZone
             
             # Find all active zones in this location (simplified lookup)
             zones = IrrigationZone.query.filter(IrrigationZone.name.contains(location)).all()
             for z in zones:
                 z.fertigation_enabled = False
                 z.status = "closed"
                 db.session.add(z)
             db.session.commit()

             AlertRegistry.register_alert(
                title="Heavy Rainfall Warning - FERTIGATION PAUSED",
                message=f"Intense rainfall ({weather.rainfall}mm) in {location}. Chemical injection halted to prevent leaching.",
                category="WEATHER",
                priority="CRITICAL",
                group_key=f"rain_{location}"
            )
            
        # Insurance Risk Trigger (L3-1557)
        from backend.models.weather import RiskTrigger
        from backend.models.insurance import InsurancePolicy
        from backend.services.risk_adjustment_service import RiskAdjustmentService
        
        # Check if weather exceeds any active risk triggers
        triggers = RiskTrigger.query.filter_by(is_active=True).all()
        for t in triggers:
            is_triggered = False
            if t.max_temp_threshold and weather.temperature > t.max_temp_threshold: is_triggered = True
            if t.max_rainfall_threshold and weather.rainfall > t.max_rainfall_threshold: is_triggered = True
            
            if is_triggered:
                # Recalculate all policies for this specific crop/location
                affected_policies = InsurancePolicy.query.filter_by(
                    crop_type=t.crop_type, 
                    farm_location=location,
                    status='ACTIVE'
                ).all()
                for p in affected_policies:
                    RiskAdjustmentService.calculate_actuarial_flux(p.id)

        return weather

    @staticmethod
    def get_latest_weather(location):
        """Get most recent weather entry from DB or fetch new if stale"""
        # Consider data stale after 30 minutes
        threshold = datetime.utcnow() - timedelta(minutes=30)
        
        latest = WeatherData.query.filter(
            WeatherData.location == location,
            WeatherData.timestamp >= threshold
        ).order_by(WeatherData.timestamp.desc()).first()
        
        if latest:
            return latest
            
        return WeatherService.update_weather_for_location(location)

    @staticmethod
    def subscribe_user(user_id, crop_name, location, soil_type=None, sowing_date=None):
        """Register a user for automated advisories"""
        sub = AdvisorySubscription(
            user_id=user_id,
            crop_name=crop_name,
            location=location,
            soil_type=soil_type,
            sowing_date=sowing_date
        )
        db.session.add(sub)
        db.session.commit()
        return sub

    @staticmethod
    def get_active_subscriptions():
        """Get all users needing automated advisories"""
        return AdvisorySubscription.query.filter_by(is_active=True).all()
