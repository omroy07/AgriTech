from backend.celery_app import celery_app
from backend.models.traceability import SupplyBatch, CustodyLog
from backend.models.disease import ContainmentZone
from backend.extensions import db
import json
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.quarantine_batch_scan')
def quarantine_batch_scan():
    """
    Daily task to auto-lock batches that have passed through a containment zone.
    Implements the "Contact Tracing" requirement.
    """
    logger.info("Starting Bio-Security Batch Quarantine Scan...")
    
    active_zones = ContainmentZone.query.filter_by(enforcement_level='LOCKED').all()
    batches = SupplyBatch.query.filter_by(quarantine_status='CLEAN').all()
    
    locked_count = 0
    for batch in batches:
        is_exposed = False
        exposure_details = []
        
        # Check batch history for exposure (simplified location check)
        # In a real system, we'd check CustodyLog GPS coords against Zone geometry
        for zone in active_zones:
            # Simulated geo-fencing check
            if batch.farm_location == zone.zone_name: # Simple string match for simulation
                is_exposed = True
                exposure_details.append({
                    'zone_id': zone.id,
                    'time': zone.quarantine_start.isoformat(),
                    'type': 'DIRECT_PROXIMITY'
                })
        
        if is_exposed:
            batch.quarantine_status = 'QUARANTINED'
            batch.contact_tracing_metadata = json.dumps(exposure_details)
            batch.bio_clearance_hash = None # Revoke clearance
            
            # Log the enforcement action
            log = CustodyLog(
                batch_id=batch.id,
                handler_id=1, # Admin/System
                action='SYSTEM_QUARANTINE_ENFORCED',
                notes=f"Auto-quarantined due to exposure in {zone.zone_name}"
            )
            db.session.add(log)
            locked_count += 1
            
    db.session.commit()
    return {'status': 'completed', 'batches_locked': locked_count}

@celery_app.task(name='tasks.vector_alert_monitor')
def vector_alert_monitor():
    """
    Monitors weather thresholds for pest breeding.
    """
    # Logic to trigger alerts if Humidity > 80% and Temp > 25C
    pass
