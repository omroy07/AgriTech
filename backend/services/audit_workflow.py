from datetime import datetime
from backend.extensions import db
from backend.models.sustainability import AuditRequest, AuditStatus, CarbonPractice
import logging

logger = logging.getLogger(__name__)

class AuditWorkflow:
    @staticmethod
    def initiate_audit(practice_id):
        """Transition a practice into the auditing lifecycle"""
        existing = AuditRequest.query.filter_by(practice_id=practice_id).first()
        if existing:
            return existing, "Audit already in progress"
            
        audit = AuditRequest(
            practice_id=practice_id,
            status=AuditStatus.SUBMITTED.value
        )
        db.session.add(audit)
        db.session.commit()
        return audit, None

    @staticmethod
    def assign_auditor(audit_id, auditor_id):
        """Assign an independent auditor to a request"""
        audit = AuditRequest.query.get(audit_id)
        if audit:
            audit.auditor_id = auditor_id
            audit.status = AuditStatus.AUDITING.value
            db.session.commit()
            return True
        return False

    @staticmethod
    def finalize_audit(audit_id, status, comments=None):
        """Finalize the audit outcome (Certify or Reject)"""
        audit = AuditRequest.query.get(audit_id)
        if not audit:
            return False
            
        audit.status = status
        audit.auditor_comments = comments
        audit.processed_at = datetime.utcnow()
        
        # If certified, update the practice status
        if status == AuditStatus.CERTIFIED.value:
            practice = CarbonPractice.query.get(audit.practice_id)
            if practice:
                practice.is_verified = True
                
        db.session.commit()
        return True

    @staticmethod
    def get_pending_audits():
        """Get all audits awaiting auditor assignment or review"""
        return AuditRequest.query.filter(
            AuditRequest.status.in_([AuditStatus.SUBMITTED.value, AuditStatus.AUDITING.value])
        ).all()
