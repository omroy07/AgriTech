class PayoutCalculator:
    """
    Mathematical logic for insurance underwriting and claim settlement.
    Calculates premiums based on risk and payouts based on yield/weather variance.
    """
    
    @staticmethod
    def calculate_premium(coverage_amount, risk_score, duration_days):
        """
        Premium = (Coverage * RiskFactor * (Days / 365))
        RiskFactor ranges from 0.02 (Low Risk) to 0.15 (High Risk).
        """
        # Normalize risk_score to a factor
        risk_factor = max(0.02, min(0.15, risk_score / 100.0))
        duration_factor = duration_days / 365.0
        
        premium = coverage_amount * risk_factor * duration_factor
        return round(premium, 2)

    @staticmethod
    def calculate_claim_eligibility(reported_loss_kg, expected_yield_kg, weather_dev_score):
        """
        Determines the percentage of coverage to payout.
        Formula: (LossRatio * 0.7) + (WeatherDeviation * 0.3)
        """
        loss_ratio = max(0, min(1, reported_loss_kg / expected_yield_kg))
        # weather_dev_score (0-1) where 1 is extreme weather event
        
        payout_ratio = (loss_ratio * 0.7) + (weather_dev_score * 0.3)
        return round(payout_ratio, 4)

    @staticmethod
    def get_risk_assessment(crop_type, region_hazard_index):
        """
        Calculates a risk score (0-100) based on crop sensitivity and regional history.
        """
        SENSITIVITY = {
            'Wheat': 30,
            'Rice': 60,   # High water dependence
            'Coffee': 80, # Sensitive to temp fluctuations
            'Corn': 45
        }
        
        base_risk = SENSITIVITY.get(crop_type, 50)
        # Final Score = (Base + Regional Hazard) / 2
        return (base_risk + region_hazard_index) / 2
