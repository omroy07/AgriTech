from datetime import datetime
import json
from backend.extensions import db
from backend.models.soil_health import SoilTest, FertilizerRecommendation, ApplicationLog
from backend.utils.nutrient_formulas import NutrientFormulas

class SoilService:
    @staticmethod
    def log_soil_test(farm_id, data):
        """Logs a new soil test result and triggers recommendation generation."""
        try:
            test = SoilTest(
                farm_id=farm_id,
                nitrogen=data['nitrogen'],
                phosphorus=data['phosphorus'],
                potassium=data['potassium'],
                ph_level=data['ph_level'],
                organic_matter=data.get('organic_matter'),
                electrical_conductivity=data.get('ec'),
                lab_name=data.get('lab_name'),
                report_url=data.get('report_url')
            )
            db.session.add(test)
            db.session.flush()
            
            # Generate recommendations for common crops
            crops = ['Wheat', 'Rice', 'Corn']
            for crop in crops:
                SoilService.generate_recommendation(test.id, crop)
            
            db.session.commit()
            return test, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def generate_recommendation(test_id, crop_type):
        """Generates crop-specific fertilizer recommendations based on a soil test."""
        test = SoilTest.query.get(test_id)
        if not test:
            return None
        
        targets = NutrientFormulas.get_crop_targets(crop_type)
        n_gap = NutrientFormulas.calculate_nutrient_gap(test.nitrogen, targets['N'])
        p_gap = NutrientFormulas.calculate_nutrient_gap(test.phosphorus, targets['P'])
        k_gap = NutrientFormulas.calculate_nutrient_gap(test.potassium, targets['K'])
        
        lime = NutrientFormulas.calculate_lime_requirement(test.ph_level)
        
        # Suggest actual fertilizers
        suggestions = []
        if n_gap > 0:
            suggestions.append({"name": "Urea", "amount": NutrientFormulas.calculate_fertilizer_amount(n_gap, 46)})
        if p_gap > 0:
            suggestions.append({"name": "DAP", "amount": NutrientFormulas.calculate_fertilizer_amount(p_gap, 46)})
        if k_gap > 0:
            suggestions.append({"name": "MOP", "amount": NutrientFormulas.calculate_fertilizer_amount(k_gap, 60)})
            
        rec = FertilizerRecommendation(
            soil_test_id=test_id,
            crop_type=crop_type,
            rec_nitrogen=n_gap,
            rec_phosphorus=p_gap,
            rec_potassium=k_gap,
            lime_requirement=lime,
            suggested_fertilizers=json.dumps(suggestions)
        )
        db.session.add(rec)
        return rec

    @staticmethod
    def get_farm_soil_history(farm_id):
        """Retrieves soil nutrient trends for a specific farm."""
        return SoilTest.query.filter_by(farm_id=farm_id).order_by(SoilTest.test_date.desc()).all()

    @staticmethod
    def log_application(soil_test_id, user_id, data):
        """Logs actual fertilizer application based on a recommendation."""
        log = ApplicationLog(
            soil_test_id=soil_test_id,
            applied_by=user_id,
            fertilizer_name=data['fertilizer_name'],
            amount_applied=data['amount'],
            area_covered=data['area'],
            notes=data.get('notes')
        )
        db.session.add(log)
        db.session.commit()
        return log
