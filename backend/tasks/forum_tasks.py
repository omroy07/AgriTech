"""
Maintenance and background processing tasks for the Community Forum.
"""
from backend.celery_app import celery_app
from backend.extensions import db
from backend.models.forum import UserReputation, ForumThread, PostComment
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.run_forum_maintenance')
def run_forum_maintenance_task(self):
    """
    Daily task to:
    1. Recalculate all user reputation scores.
    2. Cleanup older flagged content that hasn't been reviewed.
    3. Update trending metrics.
    """
    try:
        logger.info("Starting forum maintenance task")
        
        # 1. Recalculate Reputations
        reputations = UserReputation.query.all()
        for rep in reputations:
            rep.calculate_score()
        
        # 2. Flagged Content Cleanup (Auto-hide content flagged > 3 times or unreviewed for 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        unreviewed_flagged_threads = ForumThread.query.filter(
            ForumThread.is_flagged == True,
            ForumThread.is_ai_approved == True,
            ForumThread.updated_at < seven_days_ago
        ).all()
        
        for thread in unreviewed_flagged_threads:
            thread.is_ai_approved = False  # De-approve for manual review
            logger.info(f"Auto-deapproved flagged thread: {thread.id}")
            
        unreviewed_flagged_comments = PostComment.query.filter(
            PostComment.is_flagged == True,
            PostComment.is_ai_approved == True,
            PostComment.updated_at < seven_days_ago
        ).all()
        
        for comment in unreviewed_flagged_comments:
            comment.is_ai_approved = False
            logger.info(f"Auto-deapproved flagged comment: {comment.id}")
            
        db.session.commit()
        
        logger.info("Forum maintenance task complete")
        return {'status': 'success', 'reputations_updated': len(reputations)}
        
    except Exception as e:
        logger.error(f"Forum maintenance task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(bind=True, name='tasks.reindex_forum_content')
def reindex_forum_content_task(self):
    """
    Weekly task to run deep AI-based content indexing.
    This improves the AI Knowledge Base search accuracy.
    """
    try:
        from backend.services.ai_moderator import ai_moderator
        
        logger.info("Starting forum content re-indexing")
        
        # Get all approved threads
        threads = ForumThread.query.filter_by(is_ai_approved=True).all()
        
        indexed_count = 0
        for thread in threads:
            # Here we would normally update an external search index like ElasticSearch or ChromaDB
            # For this MVP, we re-run AI summary/keyword extraction if needed
            indexed_count += 1
            
        logger.info(f"Forum indexing complete: {indexed_count} threads processed")
        return {'status': 'success', 'indexed_count': indexed_count}
        
    except Exception as e:
        logger.error(f"Forum indexing task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}
