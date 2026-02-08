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
            weather_condition=raw_data['weather'][0]['main']
        )
        
        db.session.add(weather)
        db.session.commit()
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
