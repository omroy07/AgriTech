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
             AlertRegistry.register_alert(
                title="Heavy Rainfall Warning",
                message=f"Intense rainfall detected in {location}. Check drainage systems.",
                category="WEATHER",
                priority="CRITICAL",
                group_key=f"rain_{location}"
            )
            
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
