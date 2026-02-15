from backend.celery_app import celery_app
from backend.services.transparency_service import TransparencyService
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.hourly_freshness_pricing_update')
def hourly_freshness_pricing_update():
    """
    Task to run hourly to adjust all produce prices based on nutritional decay algorithm.
    """
    logger.info("Starting hourly freshness-based pricing adjustment...")
    try:
        count = TransparencyService.run_hourly_pricing_adjustment()
        logger.info(f"Successfully adjusted prices for {count} stock items.")
        return {'status': 'success', 'adjusted_count': count}
    except Exception as e:
        logger.error(f"Failed to adjust prices: {str(e)}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task(name='tasks.sync_reputation_feedback')
def sync_reputation_feedback():
    """
    Periodic check to ensure all new reviews are factored into farmer reputations.
    (Self-healing if manual review processing missed any).
    """
    pass # Managed synchronously in this L3 impl, but hook remains for scale.
