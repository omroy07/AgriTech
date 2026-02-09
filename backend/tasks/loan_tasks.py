from backend.celery_app import celery_app
from backend.models.loan_v2 import RepaymentSchedule, CollectionNote
from backend.models.loan_request import LoanRequest
from backend.services.loan_scheduler import LoanScheduler
from backend.extensions import db
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.daily_payment_reminders')
def daily_payment_reminders_task():
    """
    Sends payment reminders for installments due in the next 3 days.
    """
    three_days_ahead = date.today() + timedelta(days=3)
    upcoming = RepaymentSchedule.query.filter(
        RepaymentSchedule.is_paid == False,
        RepaymentSchedule.due_date <= three_days_ahead,
        RepaymentSchedule.due_date >= date.today()
    ).all()
    
    for schedule in upcoming:
        logger.info(f"Sending payment reminder for Loan #{schedule.loan_request_id}, Installment #{schedule.installment_number}")
        # In real app: send email/SMS
    
    return {'status': 'success', 'reminders_sent': len(upcoming)}

@celery_app.task(name='tasks.overdue_escalation')
def overdue_escalation_task():
    """
    Escalates collection efforts for loans overdue by 7+ days.
    """
    seven_days_ago = date.today() - timedelta(days=7)
    overdue = RepaymentSchedule.query.filter(
        RepaymentSchedule.is_paid == False,
        RepaymentSchedule.due_date <= seven_days_ago
    ).all()
    
    escalated = 0
    for schedule in overdue:
        # Check if collection note already exists
        existing = CollectionNote.query.filter_by(
            loan_request_id=schedule.loan_request_id,
            note_type='WARNING'
        ).first()
        
        if not existing:
            note = CollectionNote(
                loan_request_id=schedule.loan_request_id,
                created_by=1,  # System user
                note_type='WARNING',
                content=f"Installment #{schedule.installment_number} is {(date.today() - schedule.due_date).days} days overdue."
            )
            db.session.add(note)
            escalated += 1
    
    db.session.commit()
    return {'status': 'success', 'escalated': escalated}

@celery_app.task(name='tasks.monthly_risk_recalculation')
def monthly_risk_recalculation_task():
    """
    Recalculates default risk scores for all active loans monthly.
    """
    active_loans = LoanRequest.query.filter_by(status='APPROVED').all()
    
    for loan in active_loans:
        LoanScheduler.update_risk_score(loan.id)
        logger.info(f"Risk score updated for Loan #{loan.id}")
    
    return {'status': 'success', 'loans_processed': len(active_loans)}
