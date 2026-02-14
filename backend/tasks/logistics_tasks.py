from backend.celery_app import celery_app
from backend.models.logistics_v2 import DeliveryVehicle, TransportRoute, DriverProfile
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.check_fleet_maintenance')
def check_fleet_maintenance_task():
    """
    Checks vehicle mileage and maintenance dates to trigger alerts.
    """
    # Trigger maintenance alert every 10,000km or 6 months
    maintenance_mileage = 10000.0
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    vehicles = DeliveryVehicle.query.filter(
        (DeliveryVehicle.mileage % maintenance_mileage < 500) | # Nearing interval
        (DeliveryVehicle.last_maintenance_date < six_months_ago) |
        (DeliveryVehicle.last_maintenance_date.is_(None))
    ).all()
    
    for v in vehicles:
        logger.warning(f"Maintenance Required: Vehicle {v.plate_number} (Mileage: {v.mileage}km)")
        # In real app: send alert to operations manager
        
    return {'status': 'success', 'alerts_sent': len(vehicles)}

@celery_app.task(name='tasks.optimize_daily_routes')
def optimize_daily_routes_task():
    """
    Simulates a daily route optimization sweep for pending dispatches.
    """
    pending_routes = TransportRoute.query.filter_by(status='PENDING').all()
    # Logic to consolidate routes or suggest better driver pairings
    return {'status': 'success', 'optimized_count': len(pending_routes)}

@celery_app.task(name='tasks.generate_fuel_efficiency_report')
def generate_fuel_efficiency_report_task():
    """
    Calculates monthly fuel efficiency across the fleet.
    """
    vehicles = DeliveryVehicle.query.all()
    efficiency_stats = []
    
    for v in vehicles:
        # Conceptual: sum of (estimated fuel / actual fuel used)
        efficiency_stats.append({'vehicle': v.plate_number, 'score': 85.0}) # Mock stat
        
    return {'status': 'success', 'report_generated': True}
