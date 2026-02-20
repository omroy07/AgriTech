import pytest
from app import app
from backend.extensions import db
from backend.models import User, SupplyBatch, CustodyLog, QualityGrade, BatchStatus
from backend.services.traceability_service import TraceabilityService
import json

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
def setup_users(test_client):
    with app.app_context():
        farmer = User(username='farmer1', email='farmer@test.com', full_name='Farmer Test', role='farmer')
        farmer.set_password('password')
        
        inspector = User(username='inspector1', email='inspector@test.com', full_name='Inspector Test', role='consultant')
        inspector.set_password('password')
        
        db.session.add(farmer)
        db.session.add(inspector)
        db.session.commit()
        return farmer.id, inspector.id

def test_full_traceability_workflow(setup_users):
    farmer_id, inspector_id = setup_users
    
    # 1. Create Batch (Service Level)
    batch, error = TraceabilityService.create_batch(
        farmer_id=farmer_id,
        crop_name='Organic Wheat',
        quantity=500.0,
        farm_location='Punjab, India',
        crop_variety='PBW 343'
    )
    
    assert error is None
    assert batch.batch_internal_id.startswith('AGRI-')
    assert batch.status == BatchStatus.HARVESTED
    assert batch.current_handler_id == farmer_id
    
    # 2. Add Quality Check
    batch, error = TraceabilityService.add_quality_check(
        batch_id=batch.batch_internal_id,
        inspector_id=inspector_id,
        grade='A',
        parameters={'moisture': 12, 'purity': 99},
        notes='Excellent quality'
    )
    
    assert error is None
    assert batch.status == BatchStatus.QUALITY_CHECK
    assert batch.is_certified is False # Certificate task is async, so still False initially
    
    # 3. Transfer Custody
    distributor_id = 999 # Mock distributor ID
    batch, error = TraceabilityService.transfer_custody(
        batch_id=batch.batch_internal_id,
        current_handler_id=farmer_id,
        new_handler_id=distributor_id,
        new_status=BatchStatus.LOGISTICS,
        location='Ludhiana Hub',
        notes='Handed over to logistics team'
    )
    
    assert error is None
    assert batch.current_handler_id == distributor_id
    assert batch.status == BatchStatus.LOGISTICS
    
    # 4. Verify Integrity and Audit Trail
    history, error = TraceabilityService.get_batch_history(batch.batch_internal_id)
    assert error is None
    assert len(history['logs']) == 3 # Harvest + Quality + Transfer
    assert history['integrity_hash'] is not None
    
    # Check log order (most recent first in to_dict)
    latest_log = history['logs'][0]
    assert latest_log['action'] == 'CUSTODY_TRANSFER'
    assert latest_log['to_status'] == BatchStatus.LOGISTICS

def test_unauthorized_transfer(setup_users):
    farmer_id, inspector_id = setup_users
    
    batch, _ = TraceabilityService.create_batch(
        farmer_id=farmer_id,
        crop_name='Rice',
        quantity=100.0,
        farm_location='Hariyana'
    )
    
    # Attempt transfer by non-handler (inspector)
    _, error = TraceabilityService.transfer_custody(
        batch_id=batch.batch_internal_id,
        current_handler_id=inspector_id, # Not the current handler
        new_handler_id=888,
        new_status=BatchStatus.PACKAGED,
        location='Warehouse A'
    )
    
    assert "Unauthorized" in error
