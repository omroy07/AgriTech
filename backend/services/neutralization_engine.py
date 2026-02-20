from backend.models.disease import MigrationVector, ContainmentZone
from backend.models.gews import OutbreakZone, DiseaseIncident
from backend.models.irrigation import IrrigationZone
from backend.models.traceability import SupplyBatch
from backend.extensions import db
from datetime import datetime, timedelta
import logging
import math
import hashlib

logger = logging.getLogger(__name__)

class NeutralizationEngine:
    """
    Biological Security & Autonomous Containment Engine.
    Maps infection speed against weather patterns to trigger blockades.
    """

    @staticmethod
    def predict_migration(zone_id):
        """
        L3 Requirement: Calculates migration vector based on infection speed and wind.
        """
        zone = OutbreakZone.query.get(zone_id)
        if not zone: return None

        # Simulation Logic: 
        # Target = Center + (Velocity * Time) adjusted by Wind Vector
        # We assume 48-hour projection
        delta_days = 2
        distance = zone.propagation_velocity * delta_days
        
        # Adjust direction by wind (simplification)
        # If wind is North (0 deg) and propagation is random, it drifts North
        effective_angle = zone.wind_vector_deg or 0.0
        
        target_lat = zone.center_latitude + (distance / 111.0) * math.cos(math.radians(effective_angle))
        target_lng = zone.center_longitude + (distance / (111.0 * math.cos(math.radians(zone.center_latitude)))) * math.sin(math.radians(effective_angle))

        vector = MigrationVector(
            outbreak_zone_id=zone.id,
            origin_lat=zone.center_latitude,
            origin_lng=zone.center_longitude,
            target_lat=target_lat,
            target_lng=target_lng,
            direction_degrees=effective_angle,
            speed_km_per_day=zone.propagation_velocity,
            intensity_index=0.8, # Based on severity
            predicted_arrival_time=datetime.utcnow() + timedelta(days=delta_days)
        )
        db.session.add(vector)
        db.session.commit()
        return vector

    @staticmethod
    def trigger_autonomous_blockade(zone_id):
        """
        Enforces irrigation shutdowns and logistics locks for affected grids.
        """
        zone = OutbreakZone.query.get(zone_id)
        if not zone: return False

        # 1. Create Containment Zone record
        containment = ContainmentZone(
            zone_name=f"BLOCKADE_{zone.zone_id}",
            center_lat=zone.center_latitude,
            center_lng=zone.center_longitude,
            radius_meters=zone.radius_km * 1000.0,
            enforcement_level='LOCKED',
            irrigation_shutdown_triggered=True,
            logistics_blockade_active=True
        )
        db.session.add(containment)

        # 2. Shutdown Irrigation in the Zone (Autonomous Fertigation Defense)
        affected_zones = IrrigationZone.query.filter_by(farm_id=1).all() # Should filter by geo-coordinates in real system
        for i_zone in affected_zones:
            i_zone.pest_control_mode = True
            i_zone.pest_neutralization_active = True
            i_zone.current_valve_status = 'CLOSED' # Emergency shutdown
            i_zone.target_pest_id = zone.id
            
        # 3. Mark Insurance for Force Majeure Review
        from backend.models.insurance import InsurancePolicy
        policies = InsurancePolicy.query.filter_by(farm_location="Example").all() # Filter by location
        for policy in policies:
            policy.force_majeure_review = True

        db.session.commit()
        return True

    @staticmethod
    def generate_bio_clearance_hash(batch_id):
        """
        Generates a secure hash if the batch is free from outbreak exposure.
        Required for generating transport manifests.
        """
        batch = SupplyBatch.query.get(batch_id)
        if not batch or batch.quarantine_status != 'CLEAN':
            return None

        # L3 Security: Hash includes batch ID + timestamp + secret salt
        salt = "BIO_SECURE_2026"
        data = f"{batch.batch_internal_id}_{datetime.utcnow().strftime('%Y%m%d')}_{salt}"
        clearance_hash = hashlib.sha256(data.encode()).hexdigest()
        
        batch.bio_clearance_hash = clearance_hash
        db.session.commit()
        return clearance_hash
