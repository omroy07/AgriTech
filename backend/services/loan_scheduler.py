from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import uuid
from backend.extensions import db
from backend.models.loan_v2 import RepaymentSchedule, PaymentHistory, DefaultRiskScore, CollectionNote
from backend.models.loan_request import LoanRequest
from backend.utils.credit_scoring import CreditScoring

class LoanScheduler:
    @staticmethod
    def generate_emi_schedule(loan_id, principal, annual_rate, tenure_months):
        """
        Generates complete EMI amortization schedule for a loan.
        Uses reducing balance method.
        """
        try:
            monthly_rate = annual_rate / 12 / 100
            
            # EMI Formula: P * r * (1+r)^n / ((1+r)^n - 1)
            emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
            emi = round(emi, 2)
            
            balance = principal
            start_date = date.today()
            
            schedules = []
            for i in range(1, tenure_months + 1):
                interest = balance * monthly_rate
                principal_part = emi - interest
                balance -= principal_part
                
                due_date = start_date + relativedelta(months=i)
                
                schedule = RepaymentSchedule(
                    loan_request_id=loan_id,
                    installment_number=i,
                    due_date=due_date,
                    principal_amount=round(principal_part, 2),
                    interest_amount=round(interest, 2),
                    total_emi=emi,
                    outstanding_balance=round(max(0, balance), 2)
                )
                schedules.append(schedule)
                db.session.add(schedule)
            
            db.session.commit()
            return schedules, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def record_payment(loan_id, schedule_id, amount, payment_method='UPI'):
        """
        Records a payment and applies late fees/penalties if applicable.
        """
        try:
            schedule = RepaymentSchedule.query.get(schedule_id)
            if not schedule or schedule.is_paid:
                return None, "Invalid or already paid installment"
            
            days_late = (date.today() - schedule.due_date).days
            late_fee = CreditScoring.calculate_late_fee(schedule.total_emi, max(0, days_late))
            penalty = CreditScoring.calculate_penalty_interest(schedule.principal_amount, max(0, days_late))
            
            payment = PaymentHistory(
                loan_request_id=loan_id,
                schedule_id=schedule_id,
                amount_paid=amount,
                payment_method=payment_method,
                transaction_ref=f"TXN-{uuid.uuid4().hex[:12].upper()}",
                late_fee=late_fee,
                penalty_interest=penalty
            )
            
            schedule.is_paid = True
            db.session.add(payment)
            db.session.commit()
            
            # Recalculate risk
            LoanScheduler.update_risk_score(loan_id)
            
            return payment, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def update_risk_score(loan_id):
        """
        Recalculates default risk score based on payment history.
        """
        schedules = RepaymentSchedule.query.filter_by(loan_request_id=loan_id).all()
        payments = PaymentHistory.query.filter_by(loan_request_id=loan_id).all()
        
        # Calculate overdue days
        overdue_schedules = [s for s in schedules if not s.is_paid and s.due_date < date.today()]
        days_overdue = max([((date.today() - s.due_date).days) for s in overdue_schedules], default=0)
        
        # Calculate payment consistency
        total_due = len([s for s in schedules if s.due_date <= date.today()])
        on_time = len([p for p in payments if p.late_fee == 0])
        consistency = CreditScoring.calculate_payment_consistency(total_due, on_time)
        
        # Loan age
        loan = LoanRequest.query.get(loan_id)
        loan_age = ((datetime.utcnow() - loan.created_at).days) // 30
        
        # Calculate probability
        prob = CreditScoring.calculate_default_probability(days_overdue, consistency, loan_age)
        risk = CreditScoring.calculate_risk_score(prob)
        
        risk_record = DefaultRiskScore(
            loan_request_id=loan_id,
            risk_score=risk,
            probability_default=prob,
            days_overdue=days_overdue,
            payment_consistency=consistency
        )
        db.session.add(risk_record)
        db.session.commit()
        return risk_record
