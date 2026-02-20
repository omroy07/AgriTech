import pytest
from app import app
from backend.extensions import db
from backend.models import User, VendorProfile, ProcurementItem, BulkOrder, OrderStatus
from backend.services.procurement_service import ProcurementService
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
def setup_procurement():
    with app.app_context():
        # Setup Buyer and Vendor
        buyer = User(username='buyer1', email='b1@test.com')
        vendor_user = User(username='vendor1', email='v1@test.com')
        db.session.add_all([buyer, vendor_user])
        db.session.commit()
        
        vendor = VendorProfile(user_id=vendor_user.id, company_name="AgriCorp Inc")
        db.session.add(vendor)
        db.session.commit()
        
        item = ProcurementItem(
            vendor_id=vendor.id,
            name="Urea Fertilizer",
            base_price=50.0,
            volume_pricing=json.dumps([{"min": 100, "price": 40.0}])
        )
        db.session.add(item)
        db.session.commit()
        
        return buyer.id, item.id

def test_pricing_and_order_flow(setup_procurement):
    buyer_id, item_id = setup_procurement
    
    # 1. Test Tiered Pricing (150 units should trigger 40.0 price)
    order, err = ProcurementService.create_order(buyer_id, item_id, 150, "Green Farm")
    assert err is None
    assert order.unit_price == 40.0
    assert order.status == OrderStatus.PROPOSED.value
    
    # 2. Test State Machine Transition (Order Vetting)
    success, err = ProcurementService.transition_order(order.id, OrderStatus.VETTED.value, "Stock confirmed")
    assert success is True
    assert order.status == OrderStatus.VETTED.value
    
    # Check History
    events = ProcurementService.get_order_history(order.id)
    assert len(events) == 2
    assert events[1].to_status == OrderStatus.VETTED.value

def test_unauthorized_order_access(setup_procurement, test_client):
    # This would normally test the API but we can test service logic or mock request
    pass
