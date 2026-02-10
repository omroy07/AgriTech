import pytest
from app import app
from backend.extensions import db
from backend.models import User, ProcessingBatch, QualityCheck, ProcessingStage
from backend.services.processing_service import ProcessingService

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
def setup_user():
    with app.app_context():
        u = User(username='op1', email='op1@factory.com')
        db.session.add(u)
        db.session.commit()
        return u.id

def test_batch_lifecycle_and_qa_gates(setup_user):
    user_id = setup_user
    
    with app.app_context():
        # 1. Create Batch
        batch, err = ProcessingService.create_batch("Wheat", 1000.0, "['Farm A', 'Farm B']")
        assert err is None
        assert batch.current_stage == ProcessingStage.COLLECTION.value
        
        # 2. Try to advance without QA (should fail)
        success, err = ProcessingService.advance_stage(batch.id, user_id, ProcessingStage.CLEANING.value)
        assert success is False
        assert "QA audit" in err
        
        # 3. Perform failing Audit (Too moist)
        audit, _ = ProcessingService.perform_audit(batch.id, user_id, 18.0, 95.0, 995.0)
        assert audit.is_passed is False
        
        # Still should fail to advance
        success, _ = ProcessingService.advance_stage(batch.id, user_id, ProcessingStage.CLEANING.value)
        assert success is False
        
        # 4. Perform passing Audit
        audit, _ = ProcessingService.perform_audit(batch.id, user_id, 12.0, 99.0, 990.0)
        assert audit.is_passed is True
        
        # 5. Advance Stage
        success, err = ProcessingService.advance_stage(batch.id, user_id, ProcessingStage.CLEANING.value)
        assert success is True
        assert batch.current_stage == ProcessingStage.CLEANING.value
        assert len(list(batch.stages)) == 2

def test_genealogy_tracking(setup_user):
    user_id = setup_user
    with app.app_context():
        batch, _ = ProcessingService.create_batch("Rice", 500.0, "[]")
        ProcessingService.perform_audit(batch.id, user_id, 11.0, 98.0, 498.0)
        ProcessingService.advance_stage(batch.id, user_id, ProcessingStage.CLEANING.value)
        
        history = ProcessingService.get_batch_genealogy(batch.id)
        assert len(history['lifecycle']) == 2
        assert len(history['audits']) == 1
        assert history['batch']['product_type'] == "Rice"
