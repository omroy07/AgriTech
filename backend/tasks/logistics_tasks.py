from datetime import datetime
from backend.services.compliance_engine import ComplianceEngine
from backend.models.logistics_v2 import TransportRoute
from backend.models.global_trade import CustomsManifest
from backend.extensions import db
from backend.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.global_tracking_sync')
def global_tracking_sync():
    """
    Real-time webhook listener simulation for international container tracking.
    Polls shipping line APIs (mocked here) and updates TransportRoute status.
    """
    logger.info("Syncing Global Logistics Containers...")
    
    # Process "IN_TRANSIT" manifests
    manifests = CustomsManifest.query.filter_by(status='CLEARED').all()
    
    updates = 0
    for man in manifests:
        # Mock logic: If cleared > 2 days ago, mark as DELIVERED
        days_in_transit = (datetime.utcnow() - man.cleared_at).days
        if days_in_transit > 2:
            man.status = 'DELIVERED'
            updates += 1
            
    db.session.commit()
    return {'status': 'completed', 'shipments_updated': updates}

@celery_app.task(name='tasks.compliance_audit_check')
def run_compliance_audit(manifest_id):
    """
    Async task triggered on manifest submission.
    Runs the heavy compliance engine checks.
    """
    result = ComplianceEngine.validate_shipment(manifest_id)
    return {'manifest_id': manifest_id, 'audit_passed': result}
