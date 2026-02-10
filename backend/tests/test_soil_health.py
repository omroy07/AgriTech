import pytest
from app import app
from backend.extensions import db
from backend.models import User, Farm, SoilTest, FertilizerRecommendation
from backend.services.soil_service import SoilService
from backend.utils.nutrient_formulas import NutrientFormulas

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
def setup_farm():
    with app.app_context():
        u = User(username='farmer2', email='f2@test.com')
        db.session.add(u)
        db.session.commit()
        
        f = Farm(name="Healthy Soil Farm", user_id=u.id)
        db.session.add(f)
        db.session.commit()
        return f.id

def test_soil_analysis_and_rec_logic(setup_farm):
    farm_id = setup_farm
    with app.app_context():
        # 1. Log a deficient soil test (Wheat target N=150, P=40, K=120)
        data = {
            'nitrogen': 50.0,
            'phosphorus': 10.0,
            'potassium': 60.0,
            'ph_level': 5.5,
            'organic_matter': 2.5,
            'ec': 1.2
        }
        test, err = SoilService.log_soil_test(farm_id, data)
        assert err is None
        assert test.id is not None
        
        # 2. Verify recommendations were generated
        recs = FertilizerRecommendation.query.filter_by(soil_test_id=test.id, crop_type='Wheat').first()
        assert recs is not None
        assert recs.rec_nitrogen == 100.0 # 150 - 50
        assert recs.rec_phosphorus == 30.0 # 40 - 10
        assert recs.rec_potassium == 60.0 # 120 - 60
        assert recs.lime_requirement > 0 # pH 5.5 < 6.5
        
        # 3. Check fertilizer suggestions (JSON)
        import json
        suggestions = json.loads(recs.suggested_fertilizers)
        assert any(s['name'] == 'Urea' for s in suggestions)
        assert any(s['name'] == 'DAP' for s in suggestions)
        assert any(s['name'] == 'MOP' for s in suggestions)

def test_nutrient_formulas():
    # Gap calculation
    assert NutrientFormulas.calculate_nutrient_gap(50, 150) == 100.0
    assert NutrientFormulas.calculate_nutrient_gap(200, 150) == 0.0
    
    # Fertilizer dosage (Need 100kg N, Urea is 46% N)
    # 100 / 0.46 = 217.39
    assert NutrientFormulas.calculate_fertilizer_amount(100, 46) == 217.39
    
    # Lime requirement (Gap of 1.0 pH)
    # (1.0 / 0.5) * 1.5 = 3.0
    assert NutrientFormulas.calculate_lime_requirement(5.5, 6.5) == 3.0
