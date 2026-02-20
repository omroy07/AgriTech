from datetime import datetime, date, timedelta
from backend.extensions import db
from backend.models.labor import WorkerProfile, WorkShift, HarvestLog, PayrollEntry
from backend.utils.payroll_formulas import PayrollFormulas

class PayrollService:
    @staticmethod
    def generate_worker_payroll(worker_id, start_date, end_date):
        """
        Generates a payroll entry for a specific worker and period.
        """
        try:
            worker = WorkerProfile.query.get(worker_id)
            if not worker:
                return None, "Worker not found"

            # 1. Calculate Hourly Pay
            shifts = WorkShift.query.filter(
                WorkShift.worker_id == worker_id,
                WorkShift.start_time >= start_date,
                WorkShift.start_time <= end_date,
                WorkShift.shift_status == 'COMPLETED'
            ).all()
            total_hours = sum([s.total_hours for s in shifts])
            base_pay, ot_pay = PayrollFormulas.calculate_hourly_pay(total_hours, worker.base_hourly_rate)

            # 2. Calculate Piece Rate Pay
            logs = HarvestLog.query.filter(
                HarvestLog.worker_id == worker_id,
                HarvestLog.logged_at >= start_date,
                HarvestLog.logged_at <= end_date,
                HarvestLog.is_processed == False
            ).all()
            total_qty = sum([l.quantity_kg for l in logs])
            piece_pay = PayrollFormulas.calculate_piece_pay(total_qty, worker.piece_rate_kg)

            # 3. Calculate Deductions & Bonus
            gross = base_pay + ot_pay + piece_pay
            tax = PayrollFormulas.calculate_tax(gross)
            
            # Simplified bonus and advances (could be fetched from elsewhere)
            bonus = 0.0
            advances = 0.0
            
            net = PayrollFormulas.calculate_net_pay(gross + bonus, tax + advances)

            payroll = PayrollEntry(
                worker_id=worker_id,
                period_start=start_date.date(),
                period_end=end_date.date(),
                gross_hourly_pay=base_pay,
                gross_piece_pay=piece_pay,
                overtime_premium=ot_pay,
                bonus_amount=bonus,
                tax_deduction=tax,
                advances_deduction=advances,
                net_payable=net
            )
            db.session.add(payroll)
            db.session.flush()

            # Mark logs as processed
            for l in logs:
                l.is_processed = True
                l.payroll_id = payroll.id

            db.session.commit()
            return payroll, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def clock_in(worker_id):
        """Starts a new work shift."""
        try:
            active_shift = WorkShift.query.filter_by(worker_id=worker_id, shift_status='ACTIVE').first()
            if active_shift:
                return None, "Shift already active"
            
            shift = WorkShift(worker_id=worker_id, start_time=datetime.utcnow())
            db.session.add(shift)
            db.session.commit()
            return shift, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def clock_out(worker_id, break_mins=0):
        """Ends the active work shift and calculates duration."""
        try:
            shift = WorkShift.query.filter_by(worker_id=worker_id, shift_status='ACTIVE').first()
            if not shift:
                return None, "No active shift found"
            
            shift.end_time = datetime.utcnow()
            shift.break_duration = break_mins
            
            duration = shift.end_time - shift.start_time
            hours = (duration.total_seconds() / 3600) - (break_mins / 60)
            shift.total_hours = round(max(0, hours), 2)
            shift.shift_status = 'COMPLETED'
            
            db.session.commit()
            return shift, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def log_harvest(worker_id, crop, qty):
        """Logs harvest quantities for a worker."""
        log = HarvestLog(worker_id=worker_id, crop_type=crop, quantity_kg=qty)
        db.session.add(log)
        db.session.commit()
        return log
