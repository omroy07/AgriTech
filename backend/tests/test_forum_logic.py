import pytest
from backend.models import ForumThread, PostComment, UserReputation, User, ForumCategory
from backend.services.forum_service import forum_service
from backend.services.ai_moderator import ai_moderator
from backend.extensions import db
from unittest.mock import patch, MagicMock

@pytest.fixture
def setup_forum_data(app):
    with app.app_context():
        # Create a test user
        user = User(username="testfarmer", email="farmer@example.com", password_hash="hash")
        db.session.add(user)
        
        # Create a category
        category = ForumCategory(name="General Farming", description="Talk about anything")
        db.session.add(category)
        db.session.commit()
        
        yield {
            'user_id': user.id,
            'category_id': category.id
        }
        
        # Cleanup
        db.session.query(PostComment).delete()
        db.session.query(ForumThread).delete()
        db.session.query(ForumCategory).delete()
        db.session.query(UserReputation).delete()
        db.session.query(User).delete()
        db.session.commit()

def test_reputation_calculation(app, setup_forum_data):
    """Test that the reputation engine calculates scores accurately"""
    with app.app_context():
        user_id = setup_forum_data['user_id']
        
        # Initial reputation
        rep = UserReputation(user_id=user_id)
        db.session.add(rep)
        db.session.commit()
        assert rep.total_score == 0
        
        # Add activities
        rep.threads_created = 2  # 2 * 5 = 10
        rep.comments_posted = 10 # 10 * 2 = 20
        rep.upvotes_received = 5 # 5 * 10 = 50
        rep.helpful_answers = 1  # 1 * 50 = 50
        
        score = rep.calculate_score()
        assert score == 130
        assert rep.is_expert is False
        
        # Test expert threshold
        rep.helpful_answers = 10 # 10 * 50 = 500
        rep.calculate_score()
        assert rep.is_expert is True

@patch('backend.services.ai_moderator.AIModerator.analyze_sentiment')
def test_ai_moderation_flagging(mock_analyze, app, setup_forum_data):
    """Test that toxic content is automatically flagged by the AI service"""
    with app.app_context():
        user_id = setup_forum_data['user_id']
        category_id = setup_forum_data['category_id']
        
        # Mock toxic response
        mock_analyze.return_value = {
            'sentiment_score': -0.9,
            'toxicity_score': 0.85,
            'is_approved': False,
            'moderation_reason': 'Contains verbal abuse'
        }
        
        thread, error = forum_service.create_thread(
            user_id=user_id,
            category_id=category_id,
            title="Toxic Title",
            content="Aggressive and harmful content here."
        )
        
        assert thread.is_flagged is True
        assert "AI Auto-flagged" in thread.flag_reason
        assert thread.is_ai_approved is False

@patch('backend.services.ai_moderator.AIModerator.generate_auto_answer')
@patch('backend.services.ai_moderator.AIModerator.analyze_sentiment')
def test_auto_answer_generation(mock_analyze, mock_answer, app, setup_forum_data):
    """Test that helpful FAQs get an automatic AI response"""
    with app.app_context():
        user_id = setup_forum_data['user_id']
        category_id = setup_forum_data['category_id']
        
        mock_analyze.return_value = {
            'sentiment_score': 0.1,
            'toxicity_score': 0.05,
            'is_approved': True,
            'moderation_reason': ''
        }
        
        mock_answer.return_value = {
            'content': 'This is an AI generated helpful guide on planting rice.',
            'confidence': 0.9,
            'category': 'planting_timing',
            'is_ai_generated': True
        }
        
        thread, error = forum_service.create_thread(
            user_id=user_id,
            category_id=category_id,
            title="When to plant rice in Maharashtra?",
            content="Looking for advice on the best months."
        )
        
        # Verify AI comment was created
        ai_comment = PostComment.query.filter_by(thread_id=thread.id, is_ai_generated=True).first()
        assert ai_comment is not None
        assert "AI generated helpful guide" in ai_comment.content

def test_threading_and_upvoting(app, setup_forum_data):
    """Test nested comments and upvote synchronization"""
    with app.app_context():
        user_id = setup_forum_data['user_id']
        category_id = setup_forum_data['category_id']
        
        # Create thread
        thread, _ = forum_service.create_thread(user_id, category_id, "T1", "C1")
        
        # Create comment
        comment, _ = forum_service.create_comment(user_id, thread.id, "Root Comment")
        
        # Create reply
        reply, _ = forum_service.create_comment(user_id, thread.id, "Reply to Root", parent_id=comment.id)
        
        assert reply.parent_id == comment.id
        
        # Test upvote
        res, _ = forum_service.toggle_upvote(user_id, comment_id=comment.id)
        assert res['action'] == 'added'
        assert comment.upvote_count == 1
        
        # Verify author reputation update
        rep = UserReputation.query.filter_by(user_id=user_id).first()
        assert rep.upvotes_received == 1

def test_forum_search_logic(app, setup_forum_data):
    """Test filtering and search indexing logic"""
    with app.app_context():
        user_id = setup_forum_data['user_id']
        category_id = setup_forum_data['category_id']
        
        # Create multi-context threads
        forum_service.create_thread(user_id, category_id, "Wheat Pests", "How to kill bugs", tags=["pests", "wheat"])
        forum_service.create_thread(user_id, category_id, "Rice Harvest", "When to cut crops", tags=["harvest", "rice"])
        
        # Search by query
        results, _ = forum_service.search_threads(query="Wheat")
        assert len(results) == 1
        assert "Wheat Pests" in results[0]['title']
        
        # Search by tag
        results, _ = forum_service.search_threads(tags=["rice"])
        assert len(results) == 1
        assert "Rice Harvest" in results[0]['title']
