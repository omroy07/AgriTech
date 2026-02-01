"""
Test Suite for Supply Chain Traceability Feature
Tests batch lifecycle, QR generation, and API endpoints
"""

import pytest
import json
from datetime import datetime
from backend.models import ProduceBatch, AuditTrail, BatchStatus, User, UserRole
from backend.services.batch_service import BatchService
from backend.utils.qr_generator import get_qr_generator


class TestBatchModels:
    """Test ProduceBatch and AuditTrail models"""
    
    def test_batch_status_validation(self):
        """Test BatchStatus enum validation"""
        assert BatchStatus.is_valid(BatchStatus.HARVESTED)
        assert BatchStatus.is_valid(BatchStatus.QUALITY_CHECK)
        assert BatchStatus.is_valid(BatchStatus.LOGISTICS)
        assert BatchStatus.is_valid(BatchStatus.IN_SHOP)
        assert not BatchStatus.is_valid("INVALID_STATUS")
    
    def test_batch_can_transition_farmer(self, db_session):
        """Test state transitions for farmer role"""
        batch = ProduceBatch(
            batch_id="TEST-001",
            qr_code="test_qr",
            produce_name="Tomatoes",
            produce_type="vegetable",
            quantity_kg=100,
            origin_location="Test Farm",
            status=BatchStatus.HARVESTED,
            farmer_id=1,
            harvest_date=datetime.utcnow()
        )
        
        # Farmer can transition Harvested -> Quality_Check
        assert batch.can_transition_to(BatchStatus.QUALITY_CHECK, UserRole.FARMER)
        
        # Farmer cannot transition Harvested -> In_Shop
        assert not batch.can_transition_to(BatchStatus.IN_SHOP, UserRole.FARMER)
    
    def test_batch_can_transition_shopkeeper(self, db_session):
        """Test state transitions for shopkeeper role"""
        batch = ProduceBatch(
            batch_id="TEST-002",
            qr_code="test_qr",
            produce_name="Tomatoes",
            produce_type="vegetable",
            quantity_kg=100,
            origin_location="Test Farm",
            status=BatchStatus.LOGISTICS,
            farmer_id=1,
            harvest_date=datetime.utcnow()
        )
        
        # Shopkeeper can transition Logistics -> In_Shop
        assert batch.can_transition_to(BatchStatus.IN_SHOP, UserRole.SHOPKEEPER)
        
        # Shopkeeper cannot transition Logistics -> Quality_Check
        assert not batch.can_transition_to(BatchStatus.QUALITY_CHECK, UserRole.SHOPKEEPER)


class TestQRGenerator:
    """Test QR code generation and verification"""
    
    def test_qr_generation(self):
        """Test QR code generation"""
        generator = get_qr_generator()
        
        qr_image, encrypted_data = generator.generate_batch_qr(
            batch_id="TEST-QR-001",
            produce_name="Organic Tomatoes",
            harvest_date=datetime(2026, 1, 30),
            farmer_id=1,
            origin_location="Green Valley Farm"
        )
        
        assert qr_image.startswith("data:image/png;base64,")
        assert len(encrypted_data) > 0
    
    def test_qr_verification(self):
        """Test QR code verification and tamper detection"""
        generator = get_qr_generator()
        
        # Generate QR
        _, encrypted_data = generator.generate_batch_qr(
            batch_id="TEST-QR-002",
            produce_name="Organic Tomatoes",
            harvest_date=datetime(2026, 1, 30),
            farmer_id=1,
            origin_location="Green Valley Farm"
        )
        
        # Verify QR
        decoded = generator.verify_and_decode_qr(encrypted_data)
        
        assert decoded is not None
        assert decoded['batch_id'] == "TEST-QR-002"
        assert decoded['produce_name'] == "Organic Tomatoes"
        assert decoded['verified'] is True
    
    def test_qr_tamper_detection(self):
        """Test that tampered QR codes are detected"""
        generator = get_qr_generator()
        
        # Try to verify invalid data
        decoded = generator.verify_and_decode_qr("invalid_encrypted_data")
        assert decoded is None


class TestBatchService:
    """Test BatchService business logic"""
    
    @pytest.fixture
    def test_farmer(self, db_session):
        """Create test farmer user"""
        farmer = User(
            username="test_farmer",
            email="test.farmer@example.com",
            role=UserRole.FARMER
        )
        db_session.add(farmer)
        db_session.commit()
        return farmer
    
    @pytest.fixture
    def test_shopkeeper(self, db_session):
        """Create test shopkeeper user"""
        shopkeeper = User(
            username="test_shopkeeper",
            email="test.shopkeeper@example.com",
            role=UserRole.SHOPKEEPER
        )
        db_session.add(shopkeeper)
        db_session.commit()
        return shopkeeper
    
    def test_create_batch(self, db_session, test_farmer):
        """Test batch creation"""
        batch, error = BatchService.create_batch(
            user_id=test_farmer.id,
            produce_name="Organic Tomatoes",
            produce_type="vegetable",
            quantity_kg=150.5,
            origin_location="Green Valley Farm"
        )
        
        assert error is None
        assert batch is not None
        assert batch.batch_id.startswith("BATCH-")
        assert batch.status == BatchStatus.HARVESTED
        assert batch.farmer_id == test_farmer.id
    
    def test_create_batch_non_farmer(self, db_session, test_shopkeeper):
        """Test that non-farmers cannot create batches"""
        batch, error = BatchService.create_batch(
            user_id=test_shopkeeper.id,
            produce_name="Tomatoes",
            produce_type="vegetable",
            quantity_kg=100,
            origin_location="Test Farm"
        )
        
        assert batch is None
        assert "Only farmers can create" in error
    
    def test_transition_batch_status(self, db_session, test_farmer):
        """Test batch status transition"""
        # Create batch
        batch, _ = BatchService.create_batch(
            user_id=test_farmer.id,
            produce_name="Tomatoes",
            produce_type="vegetable",
            quantity_kg=100,
            origin_location="Test Farm"
        )
        
        # Transition to Quality_Check
        success, message = BatchService.transition_batch_status(
            batch_id=batch.batch_id,
            new_status=BatchStatus.QUALITY_CHECK,
            user_id=test_farmer.id,
            notes="Quality inspection passed"
        )
        
        assert success is True
        assert "updated to Quality_Check" in message
        
        # Verify status changed
        updated_batch = BatchService.get_batch_by_id(batch.batch_id)
        assert updated_batch.status == BatchStatus.QUALITY_CHECK
    
    def test_unauthorized_transition(self, db_session, test_farmer, test_shopkeeper):
        """Test that unauthorized transitions are blocked"""
        # Create batch as farmer
        batch, _ = BatchService.create_batch(
            user_id=test_farmer.id,
            produce_name="Tomatoes",
            produce_type="vegetable",
            quantity_kg=100,
            origin_location="Test Farm"
        )
        
        # Try to transition to In_Shop as shopkeeper (should fail - wrong status)
        success, message = BatchService.transition_batch_status(
            batch_id=batch.batch_id,
            new_status=BatchStatus.IN_SHOP,
            user_id=test_shopkeeper.id
        )
        
        assert success is False
        assert "cannot transition" in message.lower()
    
    def test_update_quality_info(self, db_session, test_farmer):
        """Test quality information update"""
        # Create batch
        batch, _ = BatchService.create_batch(
            user_id=test_farmer.id,
            produce_name="Tomatoes",
            produce_type="vegetable",
            quantity_kg=100,
            origin_location="Test Farm"
        )
        
        # Update quality
        success, message = BatchService.update_quality_info(
            batch_id=batch.batch_id,
            quality_grade="A",
            quality_notes="Excellent quality, no defects",
            user_id=test_farmer.id
        )
        
        assert success is True
        
        # Verify update
        updated_batch = BatchService.get_batch_by_id(batch.batch_id)
        assert updated_batch.quality_grade == "A"
        assert "Excellent quality" in updated_batch.quality_notes
    
    def test_get_batches_by_farmer(self, db_session, test_farmer):
        """Test retrieving batches by farmer"""
        # Create multiple batches
        for i in range(3):
            BatchService.create_batch(
                user_id=test_farmer.id,
                produce_name=f"Crop {i}",
                produce_type="vegetable",
                quantity_kg=100,
                origin_location="Test Farm"
            )
        
        # Retrieve batches
        batches = BatchService.get_batches_by_farmer(test_farmer.id)
        
        assert len(batches) == 3
    
    def test_audit_trail_creation(self, db_session, test_farmer):
        """Test that audit logs are created for batch operations"""
        # Create batch
        batch, _ = BatchService.create_batch(
            user_id=test_farmer.id,
            produce_name="Tomatoes",
            produce_type="vegetable",
            quantity_kg=100,
            origin_location="Test Farm"
        )
        
        # Check audit logs
        audit_logs = AuditTrail.query.filter_by(batch_id=batch.id).all()
        
        assert len(audit_logs) == 1
        assert audit_logs[0].event_type == "BATCH_CREATED"
        assert audit_logs[0].user_id == test_farmer.id


class TestTraceabilityAPI:
    """Test Traceability API endpoints"""
    
    @pytest.fixture
    def auth_headers_farmer(self, test_farmer):
        """Generate JWT token for farmer"""
        import jwt
        import os
        
        token = jwt.encode(
            {'user_id': test_farmer.id, 'role': UserRole.FARMER, 'email': test_farmer.email},
            os.environ.get('JWT_SECRET', 'agritech_secret_key'),
            algorithm='HS256'
        )
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    def test_create_batch_endpoint(self, client, auth_headers_farmer):
        """Test POST /api/v1/traceability/batches"""
        response = client.post(
            '/api/v1/traceability/batches',
            headers=auth_headers_farmer,
            json={
                'produce_name': 'Organic Tomatoes',
                'produce_type': 'vegetable',
                'quantity_kg': 150.5,
                'origin_location': 'Green Valley Farm',
                'certification': 'organic'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'batch' in data['data']
        assert data['data']['batch']['status'] == BatchStatus.HARVESTED
    
    def test_get_batch_endpoint(self, client, auth_headers_farmer, test_batch):
        """Test GET /api/v1/traceability/batches/{batch_id}"""
        response = client.get(
            f'/api/v1/traceability/batches/{test_batch.batch_id}',
            headers=auth_headers_farmer
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['batch']['batch_id'] == test_batch.batch_id
    
    def test_public_verification_endpoint(self, client, test_batch):
        """Test GET /api/v1/traceability/verify/{batch_id} (no auth required)"""
        response = client.get(
            f'/api/v1/traceability/verify/{test_batch.batch_id}'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'passport' in data['data']
        assert data['data']['passport']['batch_id'] == test_batch.batch_id


# Pytest fixtures
@pytest.fixture
def db_session():
    """Create database session for testing"""
    from backend.extensions import db
    from app import app
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(db_session):
    """Create test client"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def test_batch(db_session, test_farmer):
    """Create a test batch"""
    batch, _ = BatchService.create_batch(
        user_id=test_farmer.id,
        produce_name="Test Tomatoes",
        produce_type="vegetable",
        quantity_kg=100,
        origin_location="Test Farm"
    )
    return batch


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
