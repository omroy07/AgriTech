from backend.celery_app import celery_app
from backend.services.weather_service import WeatherService
from backend.services.advisory_engine import AdvisoryEngine
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.fetch_weather_updates')
def fetch_weather_updates_task():
    """Periodic task to refresh weather data for popular/subscribed locations"""
    try:
        subs = WeatherService.get_active_subscriptions()
        unique_locations = {sub.location for sub in subs}
        
        for loc in unique_locations:
            WeatherService.update_weather_for_location(loc)
            
        return {'status': 'success', 'locations_updated': len(unique_locations)}
    except Exception as e:
        logger.error(f"Weather update task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task(name='tasks.generate_bulk_advisories')
def generate_bulk_advisories_task():
    """Bulk AI advisory generation for all active subscribers"""
    try:
        subs = WeatherService.get_active_subscriptions()
        count = 0
        for sub in subs:
            # We could add logic to check growth stage based on sowing date
            growth_stage = _calculate_growth_stage(sub.sowing_date)
            
            advisory = AdvisoryEngine.generate_advisory(
                user_id=sub.user_id,
                crop_name=sub.crop_name,
                location=sub.location,
                soil_type=sub.soil_type,
                growth_stage=growth_stage
            )
            if advisory: count += 1
            
        return {'status': 'success', 'advisories_sent': count}
    except Exception as e:
        logger.error(f"Bulk advisory task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def _calculate_growth_stage(sowing_date):
    """Simple rule-based growth stage estimation"""
    if not sowing_date: return "Active Growth"
    
    from datetime import date
    days_passed = (date.today() - sowing_date).days
    
    if days_passed < 15: return "Seedling"
    if days_passed < 45: return "Vegetative"
    if days_passed < 90: return "Flowering"
    return "Maturity"
