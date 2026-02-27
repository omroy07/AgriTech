from backend.celery_app import celery_app
from backend.models.carbon_escrow import CarbonTradeEscrow
from backend.services.carbon_escrow_service import CarbonEscrowManager
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.carbon_escrow_validation_sweep')
def trigger_carbon_proof_validation():
    """
    Automated background sweep of 'FUNDED' escrows to check for satellite multi-spectral validation.
    """
    logger.info("🛰️ [L3-1642] Scanning for funded carbon trades pending spectral proof...")
    
    funded_trades = CarbonTradeEscrow.query.filter_by(status='FUNDED').all()
    verified_count = 0
    
    for trade in funded_trades:
        if CarbonEscrowManager.verify_satellite_spectral_proof(trade.id):
            verified_count += 1
            
    logger.info(f"Carbon sweep complete. Verified {verified_count} trade proof hashes.")
    return {'verified': verified_count}
