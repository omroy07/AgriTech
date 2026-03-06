from backend.celery_app import celery_app
from backend.models.autonomous_supply import SmartContractOrder
from backend.services.freight_match_service import FreightMatchEngine
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.autonomous_logistics_sweep')
def logistics_matching_sweep():
    """
    Scans for orders in PENDING_TRIGGER status and attempts vehicle pairing.
    """
    logger.info("🚚 [L3-1644] Scanning for pending autonomous logistics assignments...")
    
    pending_orders = SmartContractOrder.query.filter_by(status='PENDING_TRIGGER').all()
    matches_found = 0
    
    for order in pending_orders:
        vehicle = FreightMatchEngine.assign_vehicle_to_order(order.id)
        if vehicle:
            matches_found += 1
            
    logger.info(f"Logistics sweep complete. Paired {matches_found} missions.")
    return {'matches': matches_found}
