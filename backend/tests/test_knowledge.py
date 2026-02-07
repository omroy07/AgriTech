import pytest
from app import app
from backend.extensions import db
from backend.models import User, Question, Answer, UserExpertise
from backend.services.knowledge_service import KnowledgeService
from backend.services.reputation_service import ReputationService

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def setup_users():
    with app.app_context():
        u1 = User(username='farmer1', email='f1@test.com')
        u2 = User(username='expert1', email='e1@test.com')
        db.session.add_all([u1, u2])
        db.session.commit()
        return u1.id, u2.id

def test_knowledge_flow(setup_users):
    u1_id, u2_id = setup_users
    
    # 1. Farmer asks question
    q, err = KnowledgeService.create_question(u1_id, "How to stop locusts?", "I see many locusts in my field.", "Pests")
    assert err is None
    assert q.title == "How to stop locusts?"
    
    # Check reputation u1
    exp_u1 = UserExpertise.query.filter_by(user_id=u1_id).first()
    assert exp_u1.reputation_score == 2 # ask_question points
    
    # 2. Expert answers
    ans, err = KnowledgeService.add_answer(q.id, u2_id, "Use organic neem spray at dawn.")
    assert err is None
    assert q.answer_count == 1
    
    # 3. Upvoting
    success, err = KnowledgeService.vote_item(u1_id, 'answer', ans.id)
    assert success is True
    assert ans.upvote_count == 1
    
    # Check u2 reputation
    exp_u2 = UserExpertise.query.filter_by(user_id=u2_id).first()
    # 5 (answer) + 15 (received_answer_vote) = 20
    assert exp_u2.reputation_score == 20
    
    # 4. Acceptance
    success, err = KnowledgeService.accept_answer(u1_id, ans.id)
    assert success is True
    assert q.has_accepted_answer is True
    assert exp_u2.reputation_score == 70 # 20 + 50 (accepted bonus)
