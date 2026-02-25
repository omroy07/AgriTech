"""
Precision Irrigation Orchestration Engine — L3-1640
===================================================
Autonomous irrigation management using soil moisture sensors and 
evapotranspiration projections.
"""

from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.precision_irrigation import WaterStressIndex, IrrigationValveAutomation
from backend.models.weather import WeatherData
import logging

logger = logging.getLogger(__name__)

class IrrigationOrchestrator:
    
    @staticmethod
    def calculate_water_deficit(farm_id: int, moisture: float, temp: float, humidity: float) -> float:
        """
        Penman-Monteith simplified deficit calculation.
        """
        # Baseline moisture target is 45%
        target = 45.0
        deficit = max(0.0, target - moisture)
        
        # ET correction: higher temp/lower humidity increases requirement
        et_modifier = (temp * 0.05) + ( (100 - humidity) * 0.02)
        return deficit * (1 + (et_modifier / 100))

    @staticmethod
    def process_zone_telemetry(farm_id: int, zone_id: str, moisture: float):
        """
        Evaluates moisture data and triggers valves if threshold breached.
        """
        # Fetch recent weather
        weather = WeatherData.query.filter_by(location_id=farm_id).order_by(WeatherData.timestamp.desc()).first()
        temp = weather.temperature if weather else 25.0
        humidity = weather.humidity if weather else 50.0
        
        stress_score = max(0.0, min(1.0, (45.0 - moisture) / 45.0))
        required_liters = IrrigationOrchestrator.calculate_water_deficit(farm_id, moisture, temp, humidity) * 100 # per hectare base
        
        log = WaterStressIndex(
            farm_id=farm_id,
            zone_id=zone_id,
            moisture_level_pct=moisture,
            evapotranspiration_rate=0.5, # Placeholder
            stress_score=stress_score,
            irrigation_required_liters=required_liters
        )
        db.session.add(log)
        db.session.flush()
        
        if stress_score > 0.4:
            IrrigationOrchestrator._trigger_valves(farm_id, zone_id, log.id)
            
        db.session.commit()
        return log

    @staticmethod
    def _trigger_valves(farm_id: int, zone_id: str, log_id: int):
        """
        Opens valves for specific zone.
        """
        valves = IrrigationValveAutomation.query.filter_by(farm_id=farm_id).all()
        for v in valves:
            v.status = 'OPEN'
            v.flow_rate_lpm = 15.0
            v.last_action = 'AUTO_OPEN_LOW_MOISTURE'
            v.last_action_at = datetime.utcnow()
            v.triggered_by_event_id = log_id
            
        logger.info(f"Hydrating Zone {zone_id} on Farm {farm_id} due to stress shift.")
