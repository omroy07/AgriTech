from datetime import datetime
from backend.extensions import db

class WorkerProfile(db.Model):
    __tablename__ = 'worker_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    contact_info = db.Column(db.String(255))
    worker_type = db.Column(db.String(50), default='SEASONAL') # SEASONAL, PERMANENT
    
    # Wage details
    base_hourly_rate = db.Column(db.Float, default=0.0)
    piece_rate_kg = db.Column(db.Float, default=0.0) # Rate per kg harvested
    
    bank_details = db.Column(db.Text) # JSON string
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shifts = db.relationship('WorkShift', backref='worker', lazy='dynamic')
    harvest_logs = db.relationship('HarvestLog', backref='worker', lazy='dynamic')
    payrolls = db.relationship('PayrollEntry', backref='worker', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'name': self.name,
            'worker_type': self.worker_type,
            'hourly_rate': self.base_hourly_rate,
            'piece_rate': self.piece_rate_kg,
            'active': self.is_active
        }

class WorkShift(db.Model):
    __tablename__ = 'work_shifts'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    
    break_duration = db.Column(db.Integer, default=0) # Minutes
    total_hours = db.Column(db.Float, default=0.0)
    
    shift_status = db.Column(db.String(20), default='ACTIVE') # ACTIVE, COMPLETED
    notes = db.Column(db.Text)

class HarvestLog(db.Model):
    __tablename__ = 'harvest_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    crop_type = db.Column(db.String(100), nullable=False)
    
    quantity_kg = db.Column(db.Float, nullable=False)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Linked to piece-rate calculation
    is_processed = db.Column(db.Boolean, default=False)
    payroll_id = db.Column(db.Integer, db.ForeignKey('payroll_entries.id'))

class PayrollEntry(db.Model):
    __tablename__ = 'payroll_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Financial breakdown
    gross_hourly_pay = db.Column(db.Float, default=0.0)
    gross_piece_pay = db.Column(db.Float, default=0.0)
    overtime_premium = db.Column(db.Float, default=0.0)
    bonus_amount = db.Column(db.Float, default=0.0)
    
    tax_deduction = db.Column(db.Float, default=0.0)
    advances_deduction = db.Column(db.Float, default=0.0)
    
    net_payable = db.Column(db.Float, nullable=False)
    
    # Lifecycle: GENERATED -> APPROVED -> PAID
    status = db.Column(db.String(20), default='GENERATED')
    payment_ref = db.Column(db.String(100))
    
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'worker_name': self.worker.name,
            'period': f"{self.period_start} to {self.period_end}",
            'gross': self.gross_hourly_pay + self.gross_piece_pay + self.overtime_premium + self.bonus_amount,
            'deductions': self.tax_deduction + self.advances_deduction,
            'net': self.net_payable,
            'status': self.status
        }
