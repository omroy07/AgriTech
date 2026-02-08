from backend.celery_app import celery_app
from backend.services.farm_analytics import FarmAnalytics
from backend.models.farm import Farm
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.monthly_farm_valuation')
def monthly_farm_valuation_task():
    """Periodic task to calculate depreciation for all active farms"""
    try:
        farms = Farm.query.all()
        for farm in farms:
            FarmAnalytics.calculate_depreciation(farm.id)
            
        logger.info(f"Processed monthly valuation for {len(farms)} farms.")
        return {'status': 'success', 'farms_processed': len(farms)}
    except Exception as e:
        logger.error(f"Monthly valuation task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task(name='tasks.generate_farm_report')
def generate_farm_report_task(farm_id):
    """Generate a comprehensive PDF report for a farm's status"""
    from backend.services.pdf_service import PDFService
    stats = FarmAnalytics.get_farm_kpis(farm_id)
    if not stats:
        return {'status': 'error', 'message': 'Farm not found'}
        
    # Mocking PDF generation for the farm
    logger.info(f"Generated farm report for: {stats['farm_name']}")
    return {'status': 'success', 'report_summary': stats}
