from datetime import datetime
from backend.extensions import db
from enum import Enum

class MaintenanceStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class RepairStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REPAIRING = "repairing"
    FIXED = "fixed"
    CANCELLED = "cancelled"

class EngineHourLog(db.Model):
    __tablename__ = 'engine_hour_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('rental_bookings.id'))
    
    hours_start = db.Column(db.Float, nullable=False)
    hours_end = db.Column(db.Float)
    
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def total_usage(self):
        return (self.hours_end - self.hours_start) if self.hours_end else 0

class MaintenanceCycle(db.Model):
    __tablename__ = 'maintenance_cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    service_type = db.Column(db.String(100), nullable=False) # e.g., Oil Change, Hydraulic Check
    interval_hours = db.Column(db.Float, nullable=False) # Perform every X hours
    last_service_hour = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.String(20), default=MaintenanceStatus.SCHEDULED.value)
    next_due_hour = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DamageReport(db.Model):
    __tablename__ = 'machinery_damage_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('rental_bookings.id'), nullable=False)
    
    description = db.Column(db.Text, nullable=False)
    estimated_repair_cost = db.Column(db.Float)
    
    escrow_hold_amount = db.Column(db.Float, default=0.0)
    
    is_disputed = db.Column(db.Boolean, default=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    repair_order = db.relationship('RepairOrder', backref='damage_report', uselist=False)

class RepairOrder(db.Model):
    __tablename__ = 'machinery_repair_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    damage_report_id = db.Column(db.Integer, db.ForeignKey('machinery_damage_reports.id'), nullable=False)
    
    service_center = db.Column(db.String(150))
    actual_cost = db.Column(db.Float)
    status = db.Column(db.String(20), default=RepairStatus.PENDING.value)
    
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

class AssetValueSnapshot(db.Model):
    __tablename__ = 'asset_value_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    current_book_value = db.Column(db.Float, nullable=False)
    depreciation_accumulated = db.Column(db.Float, default=0.0)
    liquidation_priority = db.Column(db.Integer) # 1 = High priority to sell
    
    # Factors
    hours_impact_factor = db.Column(db.Float)
    maintenance_health_bonus = db.Column(db.Float)
    
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'value': self.current_book_value,
            'depreciation': self.depreciation_accumulated,
            'priority': self.liquidation_priority,
            'date': self.calculated_at.isoformat()
        }

class ComponentWearMap(db.Model):
    """
    Microscopic wear tracking for individual machinery components (L3-1603).
    """
    __tablename__ = 'component_wear_maps'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    component_name = db.Column(db.String(100), nullable=False) # e.g., "Hydraulic Pump", "Transmission"
    current_wear_percentage = db.Column(db.Float, default=0.0)
    critical_threshold = db.Column(db.Float, default=85.0)
    
    last_inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    predicted_failure_date = db.Column(db.DateTime)

class MaintenanceEscrow(db.Model):
    """
    Automated financial reserve for predicted equipment repairs (L3-1603).
    """
    __tablename__ = 'maintenance_escrows'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    
    escrow_balance = db.Column(db.Float, default=0.0)
    projected_cost = db.Column(db.Float, default=0.0)
    
    is_locked = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow)
