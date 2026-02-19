from datetime import datetime, timedelta
import math
from backend.models.equipment import Equipment, MaintenanceCycle, MaintenanceStatus
from backend.models.machinery import EngineHourLog
from backend.models.reliability_log import ReliabilityLog
from backend.models.soil_health import SoilTest
from backend.models.weather import WeatherData
from backend.services.weather_service import WeatherService
from backend.models.labor import WorkerSkillMap
from backend.services.audit_service import AuditService
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class MaintenanceLogic:
    """
    heavy math for Calculating "Mean Time to Failure" (MTTF) based on soil density and recent weather.
    Correlates multiple data streams: Telemetry + Environment + Operator Skill.
    """

    @staticmethod
    def calculate_wear_factor(equipment_id, hours_operated, location):
        """
        Calculates a 'Wear Factor' multiplier (1.0 = normal, 2.0 = double wear).
        Considers Soil Density (clay/rock) and Weather (dust/mud).
        """
        wear_factor = 1.0
        
        # 1. Soil Density Impact
        # Find latest soil test near equipment location (simplified: find by Farm ID logic)
        # Using a direct query here for brevity assuming location string contains farm ID or similar
        # In production this would be geospatial.
        # Check if "Heavy Clay" or high compaction
        # For prototype: Assume wear += 0.5 if 'Clay' in soil type description (Mocked)
        is_high_density = False # ... Logic to check SoilTest
        if is_high_density:
            wear_factor += 0.5

        # 2. Weather Impact (Dust/Mud)
        history = WeatherService.get_latest_weather(location)
        if history:
            # High humidity + rain = Mud -> Strain on drivetrain
            if history.rainfall > 5 or history.humidity > 80:
                wear_factor += 0.3
            # High wind + dry = Dust -> Air filter/Engine stress
            elif history.wind_speed > 20 and history.humidity < 30:
                wear_factor += 0.4
                
        return wear_factor

    @staticmethod
    def update_reliability_score(equipment_id):
        """
        Main Engine: Re-calculates Reliability Score (0-100) based on telemetry and MTTF.
        """
        equip = Equipment.query.get(equipment_id)
        if not equip: return
        
        # 1. Base Degradation from Engine Hours
        # Get total hours
        total_hours = db.session.query(db.func.sum(EngineHourLog.hours_end - EngineHourLog.hours_start)).filter_by(equipment_id=equipment_id).scalar() or 0
        
        # Ideal lifespan (e.g., 10,000 hours)
        lifespan = 10000.0
        base_score = max(0, 100 * (1 - (total_hours / lifespan)))
        
        # 2. Telemetry Penalties (Vibration, Heat)
        penalty = 0.0
        if equip.vibration_level > 5.0: # Threshold
            penalty += (equip.vibration_level - 5.0) * 2
        if equip.heat_index > 95.0: # Overheating
            penalty += (equip.heat_index - 95.0) * 1.5
            
        current_score = base_score - penalty
        
        # 3. Apply Update
        equip.reliability_score = max(0, current_score)
        equip.last_health_check = datetime.utcnow()
        
        # 4. Log History
        log = ReliabilityLog(
            equipment_id=equip.id,
            vibration_peak=equip.vibration_level,
            temp_peak=equip.heat_index,
            calculated_reliability_score=equip.reliability_score,
            trigger_event="SYSTEM_AUDIT"
        )
        db.session.add(log)
        
        # 5. Auto-Trigger Maintenance if Score < Threshold
        if equip.reliability_score < 40.0:
            MaintenanceLogic.trigger_emergency_maintenance(equip)
            
        db.session.commit()
        return equip.reliability_score

    @staticmethod
    def trigger_emergency_maintenance(equipment):
        """Safely locks equipment and schedules immediate repair."""
        equipment.is_available = False
        
        # Check if already scheduled
        existing = MaintenanceCycle.query.filter_by(equipment_id=equipment.id, status=MaintenanceStatus.SCHEDULED.value).first()
        if not existing:
            cycle = MaintenanceCycle(
                equipment_id=equipment.id,
                service_type="EMERGENCY_REPAIR",
                interval_hours=0,
                status=MaintenanceStatus.SCHEDULED.value,
                next_due_hour=0
            )
            db.session.add(cycle)
            
        # Audit
        AuditService.log_event(
            user_id=equipment.owner_id,
            action="SAFETY_LOCKOUT",
            resource_type="EQUIPMENT",
            resource_id=equipment.id,
            details=f"Reliability {equipment.reliability_score:.1f}% < 40%. Auto-locked for safety.",
            risk_level="CRITICAL"
        )
        
        # Notify Safety Officer (Mocked)
        # NotificationService.send_alert(...) 

    @staticmethod
    def validate_operator_skill(worker_id, equipment_category):
        """
        Ensures the assigned operator has the specific certification for this heavy machinery.
        Returns: valid (bool), skill_level
        """
        # simplified mapping
        required_skill = f"{equipment_category}_Operator"
        
        skill = WorkerSkillMap.query.filter_by(worker_id=worker_id, skill_name=required_skill).first()
        
        if not skill:
            return False, None
            
        # Start expiry check
        if skill.expiry_date and skill.expiry_date < datetime.utcnow().date():
            return False, "EXPIRED"
            
        return True, skill.certification_level
