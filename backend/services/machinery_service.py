from datetime import datetime
from backend.extensions import db
from backend.models.machinery import EngineHourLog, MaintenanceCycle, DamageReport, RepairOrder, MaintenanceStatus, RepairStatus
from backend.models.equipment import Equipment, RentalBooking
from backend.utils.fleet_logic import FleetLogic
import logging

logger = logging.getLogger(__name__)

class MachineryService:
    @staticmethod
    def log_engine_hours(equipment_id, hours_start, hours_end, booking_id=None):
        """Record usage period for a machine"""
        try:
            log = EngineHourLog(
                equipment_id=equipment_id,
                booking_id=booking_id,
                hours_start=hours_start,
                hours_end=hours_end
            )
            db.session.add(log)
            
            # Update equipment total hours
            equipment = Equipment.query.get(equipment_id)
            if equipment:
                # Assuming equipment model has 'total_hours' field (we'll assume or it uses log sum)
                # For this implementation we'll assume it exists or use logs to track
                pass
            
            db.session.commit()
            return log, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def schedule_maintenance(equipment_id, service_type, interval):
        """Define a recurring maintenance requirement"""
        cycle = MaintenanceCycle(
            equipment_id=equipment_id,
            service_type=service_type,
            interval_hours=interval,
            status=MaintenanceStatus.SCHEDULED.value
        )
        db.session.add(cycle)
        db.session.commit()
        return cycle

    @staticmethod
    def report_damage(booking_id, equipment_id, description, estimate):
        """Flag machinery damage upon return and hold escrow"""
        try:
            report = DamageReport(
                booking_id=booking_id,
                equipment_id=equipment_id,
                description=description,
                estimated_repair_cost=estimate,
                escrow_hold_amount=estimate # Simplified hold logic
            )
            db.session.add(report)
            
            # Create a pending repair order
            repair = RepairOrder(
                damage_report_id=report.id,
                status=RepairStatus.PENDING.value
            )
            db.session.add(repair)
            
            db.session.commit()
            return report, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def complete_repair(repair_id, actual_cost, service_center):
        """Finalize repair and update lifecycle cost"""
        repair = RepairOrder.query.get(repair_id)
        if not repair:
            return False, "Repair order not found"
            
        repair.actual_cost = actual_cost
        repair.service_center = service_center
        repair.status = RepairStatus.FIXED.value
        repair.completed_at = datetime.utcnow()
        
        db.session.commit()
        return True, None

    @staticmethod
    def get_fleet_health(equipment_id):
        """Calculate maintenance progress and health score"""
        # Get total hours from logs
        logs = EngineHourLog.query.filter_by(equipment_id=equipment_id).all()
        total_hours = sum([l.total_usage() for l in logs])
        
        cycles = MaintenanceCycle.query.filter_by(equipment_id=equipment_id).all()
        maintenance_data = []
        
        for c in cycles:
            remaining = FleetLogic.forecast_maintenance(total_hours, c.last_service_hour, c.interval_hours)
            maintenance_data.append({
                'type': c.service_type,
                'remaining_hours': remaining,
                'is_overdue': remaining <= 0
            })
            
        return {
            'total_hours': total_hours,
            'maintenance': maintenance_data
        }
