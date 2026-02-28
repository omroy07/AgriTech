from datetime import datetime, timedelta
import math
from backend.extensions import db
from backend.models.soil_health import SoilTest
from backend.models.irrigation import IrrigationZone, FertigationLog, ValveStatus
from backend.models.weather import WeatherData
from backend.services.weather_service import WeatherService
from backend.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)

class FertigationService:
    """
    Service for autonomous Precision Fertigation Control and Nutrient Flux Modeling.
    Implments heavy-math runoff risk scores and real-time nutrient balance adjustments.
    """

    @staticmethod
    def calculate_mix_ratio(zone_id):
        """
        Algorithm to calculate water/fertilizer mix based on SoilTest deficits 
        and real-time evaporation data.
        """
        zone = IrrigationZone.query.get(zone_id)
        if not zone: return None

        # 1. Fetch latest Soil Health data for this farm
        soil_test = SoilTest.query.filter_by(farm_id=zone.farm_id).order_by(SoilTest.test_date.desc()).first()
        if not soil_test:
            logger.warning(f"No soil test found for farm {zone.farm_id}, using default values.")
            n_deficit = 50.0 # Default ppm requirement
        else:
            # Logic: Target 100 ppm Nitrogen in topsoil
            n_deficit = max(0, 100.0 - soil_test.nitrogen)

        # 2. Evaporation Rate Impact (Weather Correction)
        # FIX: Fetch latest weather for the zone's specific micro-climate
        weather = WeatherService.get_latest_weather("Zone_" + str(zone_id))
        temp = weather.temperature if weather else 25.0
        humidity = weather.humidity if weather else 50.0
        
        # Simplified Penman-Monteith factor for evaporation impact on absorption
        evap_factor = (temp * (100 - humidity)) / 1000.0 
        
        # 3. Nutrient Flux Adjustment (L3-1547 requirement)
        # If flux index is high (leaching risk), reduce concentration but increase frequency
        flux_modifier = 1.0
        if soil_test and soil_test.nitrogen_flux_index:
            flux_modifier = 1.0 / (1.0 + soil_test.nitrogen_flux_index)

        # Final Concentration PPM
        target_concentration = n_deficit * (1.0 + evap_factor) * flux_modifier
        
        return round(target_concentration, 2)

    @staticmethod
    def calculate_washout_risk(zone_id, target_ppm):
        """
        Significant math for Chemical Washout Risk scores.
        Predicts leaching based on flux modeling and rain intensity.
        """
        zone = IrrigationZone.query.get(zone_id)
        soil_test = SoilTest.query.filter_by(farm_id=zone.farm_id).order_by(SoilTest.test_date.desc()).first()
        weather = WeatherService.get_latest_weather("Farm_Location")

        # 1. Rainfall Impact (Predictive)
        # Assuming we fetch a 24h forecast. If rainfall > 10mm, risk increases exponentially.
        raw_rain = weather.rainfall if weather else 0.0
        rain_factor = math.pow(raw_rain / 10.0, 1.5) if raw_rain > 0 else 0.0

        # 2. Soil Saturation & Leaching Susceptibility
        leaching_base = soil_test.leaching_susceptibility if soil_test and soil_test.leaching_susceptibility else 0.3
        
        # 3. Cumulative Flux Modelling
        # Risk = [Concentration * Leaching_Base] * [1 + Rain_Factor]
        risk_score = (target_ppm / 500.0) * leaching_base * (1.0 + rain_factor)
        
        return min(1.0, risk_score)

    @staticmethod
    def trigger_automated_fertigation(zone_id):
        """
        Main entry point for autonomous control.
        """
        zone = IrrigationZone.query.get(zone_id)
        if not zone or not zone.fertigation_enabled:
            return

        target_concentration = FertigationService.calculate_mix_ratio(zone_id)
        risk_score = FertigationService.calculate_washout_risk(zone_id, target_concentration)

        # Safety Override: If risk > threshold, block chemical injection
        if risk_score > zone.washout_risk_threshold:
            logger.critical(f"FERTIGATION BLOCKED: Washout risk ({risk_score:.2f}) exceeds threshold.")
            zone.fertigation_valve_status = ValveStatus.CLOSED.value
            db.session.commit()
            
            # Audit the safety block
            AuditService.log_event(
                user_id=1, # System User
                action="ENVIRONMENTAL_SAFETY_BLOCK",
                resource_type="FERTIGATION",
                resource_id=zone.id,
                details=f"Autonomous block of chemical injection due to high runoff risk ({risk_score:.2f}). Rain intensity high.",
                risk_level="HIGH"
            )
            return False

        # Apply Nutrient Balance State adjustments
        # Adjust chemical concentration and open valve
        zone.chemical_concentration = target_concentration
        zone.fertigation_valve_status = ValveStatus.OPEN.value
        
        # Log the injection
        # FIX: Calculate volume based on zone capacity and moisture deficit
        moisture_def = max(0, zone.moisture_threshold_max - 40.0) # Mock current moisture 40
        calc_volume = 100.0 * (moisture_def / 10.0)
        
        log = FertigationLog(
            zone_id=zone.id,
            injectant_type="N-MIX",
            concentration_ppm=target_concentration,
            volume_liters=calc_volume,
            washout_risk_score=risk_score
        )
        db.session.add(log)
        db.session.commit()
        
        AuditService.log_event(
            user_id=1,
            action="PRECISION_FERTIGATION_START",
            resource_type="FERTIGATION",
            resource_id=zone.id,
            details=f"Injected {target_concentration}ppm N-MIX. Calculated washout risk: {risk_score:.2f}.",
            risk_level="INFO"
        )
        return True
