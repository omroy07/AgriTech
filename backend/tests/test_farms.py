import pytest
from app import app
from backend.extensions import db
from backend.models import User, Farm, FarmMember, FarmAsset, FarmRole
from backend.services.farm_service import FarmService
from backend.services.farm_analytics import FarmAnalytics

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
        u1 = User(username='owner1', email='o1@test.com')
        u2 = User(username='worker1', email='w1@test.com')
        db.session.add_all([u1, u2])
        db.session.commit()
        return u1.id, u2.id

def test_farm_creation_and_tenancy(setup_users):
    u1_id, u2_id = setup_users
    
    # 1. User creates a farm
    farm, err = FarmService.create_farm(u1_id, "Sunrise Acres", "Karnataka", 50.5)
    assert err is None
    assert farm.name == "Sunrise Acres"
    
    # 2. Check automatic ownership
    membership = FarmMember.query.filter_by(farm_id=farm.id, user_id=u1_id).first()
    assert membership.role == FarmRole.OWNER.value
    
    # 3. Add a worker
    member, err = FarmService.add_member(farm.id, u2_id, FarmRole.WORKER.value, u1_id)
    assert err is None
    assert member.user_id == u2_id
    
    # 4. Filter tenancy
    u1_farms = FarmService.get_user_farms(u1_id)
    assert len(u1_farms) == 1
    assert u1_farms[0].id == farm.id

def test_asset_tracking_and_analytics(setup_users):
    u1_id, _ = setup_users
    
    # 1. Register farm and assets
    farm, _ = FarmService.create_farm(u1_id, "TechFarm", "Pune")
    FarmService.add_asset(farm.id, "Drone X1", "Electronics", 50000.0)
    FarmService.add_asset(farm.id, "Sprinkler Jet", "Irrigation", 10000.0)
    
    # 2. Verify KPIs
    stats = FarmAnalytics.get_farm_kpis(farm.id)
    assert stats['total_asset_value'] == 60000.0
    assert stats['asset_health']['Good'] == 2
    
    # 3. Simulate Depreciation
    FarmAnalytics.calculate_depreciation(farm.id, annual_rate=0.12) # 1% monthly
    
    # Check new valuation
    asset = FarmAsset.query.filter_by(farm_id=farm.id, name="Drone X1").first()
    assert asset.current_valuation < 50000.0 # Should have dropped
    assert asset.current_valuation == 50000.0 * (1 - 0.12/12)
