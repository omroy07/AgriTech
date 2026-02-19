from datetime import datetime
from backend.celery_app import celery
from backend.extensions import db
from backend.models import Alert
from backend.utils.logger import logger

@celery.task(name='tasks.cleanup_expired_alerts')
def cleanup_expired_alerts():
    """
    Background task to remove alerts that have passed their expiration date.
    Runs periodically (e.g., daily).
    """
    try:
        now = datetime.utcnow()
        expired_count = Alert.query.filter(Alert.expires_at < now).count()
        
        if expired_count > 0:
            Alert.query.filter(Alert.expires_at < now).delete()
            db.session.commit()
            logger.info(f"Cleaned up {expired_count} expired alerts.")
        else:
            logger.info("No expired alerts to clean up.")
            
        return {'status': 'success', 'deleted': expired_count}
    except Exception as e:
        logger.error(f"Error during alert cleanup: {str(e)}")
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}

@celery.task(name='tasks.archive_old_read_alerts')
def archive_old_read_alerts(days=30):
    """
    Archives or deletes read alerts older than a certain number of days.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        old_alerts = Alert.query.filter(
            Alert.read_at.isnot(None), 
            Alert.read_at < cutoff
        ).delete()
        
        db.session.commit()
        logger.info(f"Archived {old_alerts} old read alerts.")
        return {'status': 'success', 'archived': old_alerts}
    except Exception as e:
        logger.error(f"Error during alert archiving: {str(e)}")
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}
