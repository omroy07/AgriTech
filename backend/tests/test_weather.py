import pytest
from app import app
from backend.extensions import db
from backend.models import User, WeatherData, CropAdvisory, AdvisorySubscription
from backend.services.weather_service import WeatherService
from backend.services.advisory_engine import AdvisoryEngine

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
        u = User(username='farmer_weather', email='fw@test.com')
        db.session.add(u)
        db.session.commit()
        return u.id

def test_weather_fetching_logic(test_client):
    # Test updating weather for a location
    weather = WeatherService.update_weather_for_location("Mumbai")
    assert weather is not None
    assert weather.location == "Mumbai"
    assert weather.temperature is not None
    
    # Test caching/latest logic
    cached = WeatherService.get_latest_weather("Mumbai")
    assert cached.id == weather.id

def test_advisory_generation(setup_user):
    user_id = setup_user
    with app.app_context():
        # Ensure weather exists for the location
        WeatherService.update_weather_for_location("Delhi")
        
        advisory = AdvisoryEngine.generate_advisory(
            user_id=user_id,
            crop_name="Wheat",
            location="Delhi",
            soil_type="Alluvial",
            growth_stage="Seedling"
        )
        
        assert advisory is not None
        assert advisory.crop_name == "Wheat"
        assert "irrigat" in advisory.advisory_text.lower() or "alert" in advisory.advisory_text.lower()
        assert advisory.priority in ['Normal', 'High']

def test_subscription_workflow(setup_user):
    user_id = setup_user
    with app.app_context():
        sub = WeatherService.subscribe_user(user_id, "Rice", "Punjab")
        assert sub.is_active is True
        
        active_subs = WeatherService.get_active_subscriptions()
        assert len(active_subs) == 1
        assert active_subs[0].crop_name == "Rice"
