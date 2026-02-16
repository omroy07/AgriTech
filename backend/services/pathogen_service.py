import math
from datetime import datetime, timedelta
from backend.extensions import db, socketio
from backend.models.gews import OutbreakZone, OutbreakProjection, DiseaseIncident
from backend.models.weather import WeatherData
from backend.services.weather_service import WeatherService
from backend.services.alert_registry import AlertRegistry
import logging

logger = logging.getLogger(__name__)

class PathogenPropagationService:
    """
    Service for simulating pathogen spread and managing containment strategies.
    """

    @staticmethod
    def simulate_propagation(zone_id):
        """
        Calculates pathogen velocity and transmission radius based on environmental factors.
        """
        zone = OutbreakZone.query.get(zone_id)
        if not zone:
            return None

        # 1. Fetch latest weather for wind vector
        location = f"{zone.center_latitude},{zone.center_longitude}"
        weather = WeatherService.get_latest_weather(location)
        
        # Base velocity (km/day) influenced by wind
        # Pathogens travel faster with higher wind speeds and specific directions
        wind_speed = weather.wind_speed if weather else 5.0
        wind_dir = weather.wind_direction if weather else 0.0
        
        # Calculate Propagation Velocity (Heuristic)
        # Higher humidity often aids pathogen survival, higher wind speed aids transport
        humidity_factor = (weather.humidity / 100.0) if weather else 0.5
        zone.propagation_velocity = (wind_speed * 0.2) * (1 + humidity_factor)
        zone.wind_vector_deg = wind_dir
        
        # 2. Update Transmission Radius
        # Influenced by soil connectivity (simulated) and severity
        severity_map = {'low': 1.0, 'medium': 2.0, 'high': 5.0, 'critical': 10.0}
        base_radius = severity_map.get(zone.severity_level.lower(), 2.0)
        zone.transmission_radius = base_radius * (1 + zone.soil_connectivity_score)
        
        db.session.commit()

        # 3. Generate Projections (Next 3 days)
        PathogenPropagationService._generate_projections(zone)
        
        # 4. Check for Autonomous Containment Triggers
        PathogenPropagationService._assess_containment_needs(zone)
        
        # 5. Emit real-time update for heatmap
        socketio.emit('pathogen_update', zone.to_dict(), namespace='/crisis')
        
        return zone

    @staticmethod
    def _generate_projections(zone):
        """
        Creates time-series risk points for the next 72 hours.
        """
        # Clear old projections for this zone
        OutbreakProjection.query.filter_by(outbreak_zone_id=zone.id).delete()
        
        # Path pathogens generally move in the direction of the wind
        # radians = math.radians(zone.wind_vector_deg)
        # In meteorology, wind direction is where it's COMING FROM. 
        # Pathogen moves TOWARDS (wind_dir + 180) % 360
        travel_dir = (zone.wind_vector_deg + 180) % 360
        rad = math.radians(travel_dir)
        
        # km to degrees (rough approximation)
        KM_PER_DEG_LAT = 111.0
        KM_PER_DEG_LON = 111.0 * math.cos(math.radians(zone.center_latitude))

        for hours in [24, 48, 72]:
            days = hours / 24.0
            distance = zone.propagation_velocity * days
            
            d_lat = (distance * math.cos(rad)) / KM_PER_DEG_LAT
            d_lon = (distance * math.sin(rad)) / KM_PER_DEG_LON
            
            projection = OutbreakProjection(
                outbreak_zone_id=zone.id,
                projection_time=datetime.utcnow() + timedelta(hours=hours),
                projected_latitude=zone.center_latitude + d_lat,
                projected_longitude=zone.center_longitude + d_lon,
                expected_radius=zone.radius_km + (zone.propagation_velocity * days * 0.5),
                confidence_score=max(0.1, 1.0 - (days * 0.2))
            )
            db.session.add(projection)
        
        db.session.commit()

    @staticmethod
    def _assess_containment_needs(zone):
        """
        Logic for autonomous lockdown based on risk levels.
        """
        # Threshold: Velocity > 5km/day OR Severity is High
        high_spread = zone.propagation_velocity > 5.0
        critical_severity = zone.severity_level.lower() in ['high', 'critical']
        
        new_status = 'NONE'
        if high_spread and critical_severity:
            new_status = 'FULL_QUARANTINE'
        elif critical_severity:
            new_status = 'ACCESS_RESTRICTED'
        elif high_spread:
            new_status = 'IRRIGATION_LOCKDOWN'

        if new_status != zone.containment_status and new_status != 'NONE':
            zone.containment_status = new_status
            zone.containment_applied_at = datetime.utcnow()
            
            # Register Security & Operational Alerts
            AlertRegistry.register_alert(
                title=f"AUTONOMOUS CONTAINMENT: {new_status}",
                message=f"System has triggered {new_status} for {zone.disease_name} in Zone {zone.zone_id}. Spread velocity: {zone.propagation_velocity:.2f} km/day.",
                category="SECURITY",
                priority="CRITICAL",
                group_key=f"containment_{zone.zone_id}"
            )
            
            # TODO: Call actual IoT/Physical controllers for irrigation shutoff
            logger.info(f"Containment {new_status} applied to zone {zone.zone_id}")
            
            db.session.commit()

    @staticmethod
    def get_risk_heatmap_data():
        """
        Aggregates all active zones and their projections for frontend rendering.
        """
        zones = OutbreakZone.query.filter_by(status='active').all()
        heatmap = []
        for z in zones:
            z_data = z.to_dict()
            projections = OutbreakProjection.query.filter_by(outbreak_zone_id=z.id).all()
            z_data['projections'] = [p.to_dict() for p in projections]
            heatmap.append(z_data)
        return heatmap
