from datetime import datetime
from sqlalchemy import or_, func
from backend.models import (
    ForumCategory, ForumThread, PostComment, Upvote, UserReputation, User
)
from backend.extensions import db
from backend.services.ai_moderator import ai_moderator
from backend.utils.logger import logger


class ForumService:
    """
    Core service for forum operations including search, reputation, and thread management
    """
    
    @staticmethod
    def create_category(name, description, icon=None):
        """Create a new forum category"""
        try:
            category = ForumCategory(
                name=name,
                description=description,
                icon=icon
            )
            db.session.add(category)
            db.session.commit()
            return category, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create category: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def create_thread(user_id, category_id, title, content, tags=None):
        """Create a new forum thread with AI moderation"""
        try:
            thread = ForumThread(
                user_id=user_id,
                category_id=category_id,
                title=title,
                content=content,
                tags=','.join(tags) if tags else ''
            )
            db.session.add(thread)
            db.session.flush()  # Get thread ID before moderation
            
            # AI Moderation
            moderation_result = ai_moderator.moderate_thread(thread)
            
            # Update user reputation
            ForumService.update_reputation(user_id, 'thread_created')
            
            db.session.commit()
            
            # Check if AI generated an auto-answer
            if moderation_result and isinstance(moderation_result, dict) and moderation_result.get('is_ai_generated'):
                # Create AI answer as a comment
                ai_comment = PostComment(
                    thread_id=thread.id,
                    user_id=0,  # System user
                    content=moderation_result['content'],
                    is_ai_generated=True,
                    is_ai_approved=True
                )
                db.session.add(ai_comment)
                db.session.commit()
            
            return thread, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create thread: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def create_comment(user_id, thread_id, content, parent_id=None):
        """Create a comment or reply with AI moderation"""
        try:
            comment = PostComment(
                user_id=user_id,
                thread_id=thread_id,
                content=content,
                parent_id=parent_id
            )
            db.session.add(comment)
            db.session.flush()
            
            # AI Moderation
            ai_moderator.moderate_comment(comment)
            
            # Update thread last_activity
            thread = ForumThread.query.get(thread_id)
            if thread:
                thread.last_activity = datetime.utcnow()
            
            # Update user reputation
            ForumService.update_reputation(user_id, 'comment_posted')
            
            db.session.commit()
            return comment, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create comment: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def toggle_upvote(user_id, thread_id=None, comment_id=None):
        """Toggle upvote on a thread or comment"""
        try:
            # Check if upvote already exists
            query = Upvote.query.filter_by(user_id=user_id)
            if thread_id:
                query = query.filter_by(thread_id=thread_id)
                target = ForumThread.query.get(thread_id)
            elif comment_id:
                query = query.filter_by(comment_id=comment_id)
                target = PostComment.query.get(comment_id)
            else:
                return None, "Must specify either thread_id or comment_id"
            
            existing_upvote = query.first()
            
            if existing_upvote:
                # Remove upvote
                db.session.delete(existing_upvote)
                target.upvote_count -= 1
                action = 'removed'
            else:
                # Add upvote
                upvote = Upvote(
                    user_id=user_id,
                    thread_id=thread_id,
                    comment_id=comment_id
                )
                db.session.add(upvote)
                target.upvote_count += 1
                action = 'added'
                
                # Update reputation of content author
                if thread_id:
                    ForumService.update_reputation(target.user_id, 'upvote_received')
                elif comment_id:
                    ForumService.update_reputation(target.user_id, 'upvote_received')
            
            db.session.commit()
            return {'action': action, 'upvote_count': target.upvote_count}, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to toggle upvote: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def search_threads(query, category_id=None, tags=None, sort_by='relevance', limit=20):
        """
        Search threads with multiple filters
        sort_by: 'relevance', 'recent', 'popular', 'unanswered'
        """
        try:
            # Base query
            threads_query = ForumThread.query.filter_by(is_ai_approved=True)
            
            # Category filter
            if category_id:
                threads_query = threads_query.filter_by(category_id=category_id)
            
            # Text search
            if query:
                search_filter = or_(
                    ForumThread.title.ilike(f'%{query}%'),
                    ForumThread.content.ilike(f'%{query}%'),
                    ForumThread.tags.ilike(f'%{query}%')
                )
                threads_query = threads_query.filter(search_filter)
            
            # Tag filter
            if tags:
                for tag in tags:
                    threads_query = threads_query.filter(ForumThread.tags.ilike(f'%{tag}%'))
            
            # Sorting
            if sort_by == 'recent':
                threads_query = threads_query.order_by(ForumThread.last_activity.desc())
            elif sort_by == 'popular':
                threads_query = threads_query.order_by(ForumThread.upvote_count.desc())
            elif sort_by == 'unanswered':
                # Subquery to count comments
                threads_query = threads_query.outerjoin(PostComment).group_by(ForumThread.id).having(
                    func.count(PostComment.id) == 0
                ).order_by(ForumThread.created_at.desc())
            else:  # relevance (default)
                threads_query = threads_query.order_by(ForumThread.view_count.desc(), ForumThread.upvote_count.desc())
            
            threads = threads_query.limit(limit).all()
            return [t.to_dict() for t in threads], None
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return [], str(e)
    
    @staticmethod
    def get_thread_details(thread_id, increment_view=True):
        """Get full thread details with comments"""
        try:
            thread = ForumThread.query.get(thread_id)
            if not thread:
                return None, "Thread not found"
            
            if increment_view:
                thread.view_count += 1
                db.session.commit()
            
            return thread.to_dict(include_comments=True), None
            
        except Exception as e:
            logger.error(f"Failed to get thread: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def update_reputation(user_id, action_type):
        """Update user reputation based on action"""
        try:
            reputation = UserReputation.query.filter_by(user_id=user_id).first()
            
            if not reputation:
                reputation = UserReputation(user_id=user_id)
                db.session.add(reputation)
            
            if action_type == 'thread_created':
                reputation.threads_created += 1
            elif action_type == 'comment_posted':
                reputation.comments_posted += 1
            elif action_type == 'upvote_received':
                reputation.upvotes_received += 1
            elif action_type == 'helpful_answer':
                reputation.helpful_answers += 1
            
            # Recalculate total score
            reputation.calculate_score()
            
            db.session.commit()
            return reputation, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update reputation: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_user_reputation(user_id):
        """Get user reputation details"""
        try:
            reputation = UserReputation.query.filter_by(user_id=user_id).first()
            if not reputation:
                # Create default reputation
                reputation = UserReputation(user_id=user_id)
                db.session.add(reputation)
                db.session.commit()
            
            return reputation.to_dict(), None
            
        except Exception as e:
            logger.error(f"Failed to get reputation: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_trending_threads(limit=10):
        """Get trending threads based on recent activity and engagement"""
        try:
            # Calculate a trending score: recent activity + engagement
            threads = ForumThread.query.filter_by(
                is_ai_approved=True,
                is_flagged=False
            ).order_by(
                ForumThread.last_activity.desc(),
                ForumThread.upvote_count.desc()
            ).limit(limit).all()
            
            return [t.to_dict() for t in threads], None
            
        except Exception as e:
            logger.error(f"Failed to get trending threads: {str(e)}")
            return [], str(e)
    
    @staticmethod
    def get_unanswered_threads(limit=10):
        """Get threads with no comments"""
        try:
            threads = ForumThread.query.filter_by(
                is_ai_approved=True,
                is_flagged=False
            ).outerjoin(PostComment).group_by(ForumThread.id).having(
                func.count(PostComment.id) == 0
            ).order_by(ForumThread.created_at.desc()).limit(limit).all()
            
            return [t.to_dict() for t in threads], None
            
        except Exception as e:
            logger.error(f"Failed to get unanswered threads: {str(e)}")
            return [], str(e)
    
    @staticmethod
    def flag_content(thread_id=None, comment_id=None, reason="User reported"):
        """Flag thread or comment for moderator review"""
        try:
            if thread_id:
                thread = ForumThread.query.get(thread_id)
                if thread:
                    thread.is_flagged = True
                    thread.flag_reason = reason
            elif comment_id:
                comment = PostComment.query.get(comment_id)
                if comment:
                    comment.is_flagged = True
                    comment.flag_reason = reason
            else:
                return None, "Must specify thread_id or comment_id"
            
            db.session.commit()
            return {'flagged': True}, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to flag content: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_user_stats(user_id):
        """Get comprehensive user forum statistics"""
        try:
            threads_count = ForumThread.query.filter_by(user_id=user_id).count()
            comments_count = PostComment.query.filter_by(user_id=user_id).count()
            
            reputation = UserReputation.query.filter_by(user_id=user_id).first()
            if not reputation:
                reputation = UserReputation(user_id=user_id)
                db.session.add(reputation)
                db.session.commit()
            
            return {
                'threads_count': threads_count,
                'comments_count': comments_count,
                'reputation': reputation.to_dict()
            }, None
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return None, str(e)


# Singleton instance
forum_service = ForumService()
