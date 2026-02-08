"""
Risk calculation utilities for Agri-Risk Score (ARS) computation.
Mathematical formulas and helper functions for insurance risk assessment.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class RiskCalculators:
    """Mathematical utilities for agricultural risk assessment."""
    
    # Base premium rates by crop type (percentage of coverage)
    CROP_BASE_RATES = {
        'rice': 3.5,
        'wheat': 3.0,
        'sugarcane': 4.0,
        'cotton': 4.5,
        'maize': 3.5,
        'soybean': 4.0,
        'vegetables': 5.0,
        'fruits': 5.5,
        'default': 4.0
    }
    
    # Risk multipliers by ARS score range
    RISK_MULTIPLIERS = [
        (0, 20, 0.7),      # Excellent: 30% discount
        (21, 40, 0.9),     # Good: 10% discount
        (41, 60, 1.0),     # Moderate: No change
        (61, 80, 1.3),     # High: 30% increase
        (81, 100, 1.6)     # Critical: 60% increase
    ]
    
    @staticmethod
    def calculate_ars_score(
        weather_risk: float,
        crop_success_rate: float,
        location_risk: float,
        activity_score: float,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate Agri-Risk Score (ARS) using weighted factors.
        
        Args:
            weather_risk: Weather-related risk (0-1, higher = riskier)
            crop_success_rate: Historical crop success (0-1, higher = better)
            location_risk: Location-based risk (0-1, higher = riskier)
            activity_score: Platform activity score (0-1, higher = better)
            weights: Custom weights for each factor
            
        Returns:
            float: ARS score (0-100, lower is better)
        """
        # Default weights
        if weights is None:
            weights = {
                'weather': 0.35,
                'crop_success': 0.30,
                'location': 0.25,
                'activity': 0.10
            }
        
        # Invert positive metrics (higher is better → lower risk score)
        inverted_crop_success = 1 - crop_success_rate
        inverted_activity = 1 - activity_score
        
        # Weighted sum
        ars = (
            weather_risk * weights['weather'] +
            inverted_crop_success * weights['crop_success'] +
            location_risk * weights['location'] +
            inverted_activity * weights['activity']
        )
        
        # Scale to 0-100
        return min(100, max(0, ars * 100))
    
    @staticmethod
    def calculate_weather_risk(
        rainfall_deviation: float,
        temperature_extremes: int,
        drought_days: int,
        flood_incidents: int
    ) -> float:
        """
        Calculate weather-related risk factor.
        
        Args:
            rainfall_deviation: Deviation from normal rainfall (percentage)
            temperature_extremes: Number of extreme temperature days
            drought_days: Number of drought days in season
            flood_incidents: Number of flood events
            
        Returns:
            float: Weather risk (0-1)
        """
        # Normalize each factor
        rainfall_score = min(1.0, abs(rainfall_deviation) / 100)
        temperature_score = min(1.0, temperature_extremes / 30)
        drought_score = min(1.0, drought_days / 60)
        flood_score = min(1.0, flood_incidents / 5)
        
        # Weighted average
        weather_risk = (
            rainfall_score * 0.30 +
            temperature_score * 0.25 +
            drought_score * 0.30 +
            flood_score * 0.15
        )
        
        return min(1.0, weather_risk)
    
    @staticmethod
    def calculate_crop_success_rate(
        successful_seasons: int,
        total_seasons: int,
        avg_yield_percentage: float
    ) -> float:
        """
        Calculate crop success rate.
        
        Args:
            successful_seasons: Number of successful seasons
            total_seasons: Total number of seasons
            avg_yield_percentage: Average yield as percentage of expected
            
        Returns:
            float: Success rate (0-1)
        """
        if total_seasons == 0:
            return 0.5  # Neutral score for new farmers
        
        # Season success rate
        season_rate = successful_seasons / total_seasons
        
        # Yield performance (normalized to 0-1)
        yield_factor = min(1.0, avg_yield_percentage / 100)
        
        # Combined score
        return (season_rate * 0.6 + yield_factor * 0.4)
    
    @staticmethod
    def calculate_location_risk(
        district: str,
        historical_disaster_count: int,
        soil_quality_index: float,
        irrigation_access: bool
    ) -> float:
        """
        Calculate location-based risk factor.
        
        Args:
            district: District name
            historical_disaster_count: Number of disasters in past 5 years
            soil_quality_index: Soil quality (0-1)
            irrigation_access: Whether irrigation is available
            
        Returns:
            float: Location risk (0-1)
        """
        # High-risk districts (can be expanded with actual data)
        high_risk_districts = [
            'drought_prone_1', 'flood_prone_1', 'cyclone_prone_1'
        ]
        
        district_risk = 0.7 if district.lower() in high_risk_districts else 0.3
        
        # Disaster frequency (normalized)
        disaster_risk = min(1.0, historical_disaster_count / 10)
        
        # Soil quality (inverted - poor soil = high risk)
        soil_risk = 1 - soil_quality_index
        
        # Irrigation (has irrigation = lower risk)
        irrigation_risk = 0.2 if irrigation_access else 0.8
        
        # Weighted combination
        location_risk = (
            district_risk * 0.25 +
            disaster_risk * 0.30 +
            soil_risk * 0.25 +
            irrigation_risk * 0.20
        )
        
        return min(1.0, location_risk)
    
    @staticmethod
    def calculate_activity_score(
        days_active: int,
        transactions_count: int,
        data_completeness: float
    ) -> float:
        """
        Calculate platform activity score (engagement indicator).
        
        Args:
            days_active: Number of days user has been active
            transactions_count: Number of transactions/activities
            data_completeness: Profile data completeness (0-1)
            
        Returns:
            float: Activity score (0-1)
        """
        # Activity duration score (capped at 180 days)
        duration_score = min(1.0, days_active / 180)
        
        # Transaction activity (capped at 50 transactions)
        transaction_score = min(1.0, transactions_count / 50)
        
        # Weighted combination
        activity = (
            duration_score * 0.30 +
            transaction_score * 0.40 +
            data_completeness * 0.30
        )
        
        return min(1.0, activity)
    
    @staticmethod
    def get_risk_multiplier(ars_score: float) -> float:
        """
        Get premium risk multiplier based on ARS score.
        
        Args:
            ars_score: Agri-Risk Score (0-100)
            
        Returns:
            float: Risk multiplier
        """
        for min_score, max_score, multiplier in RiskCalculators.RISK_MULTIPLIERS:
            if min_score <= ars_score <= max_score:
                return multiplier
        
        return 1.0  # Default
    
    @staticmethod
    def calculate_premium(
        coverage_amount: float,
        crop_type: str,
        ars_score: float,
        farm_size_acres: float
    ) -> Tuple[float, float, float]:
        """
        Calculate insurance premium based on risk factors.
        
        Args:
            coverage_amount: Desired coverage amount
            crop_type: Type of crop
            ars_score: Agri-Risk Score
            farm_size_acres: Farm size
            
        Returns:
            tuple: (premium_amount, base_rate, risk_multiplier)
        """
        # Get base rate for crop
        crop_key = crop_type.lower()
        base_rate = RiskCalculators.CROP_BASE_RATES.get(
            crop_key,
            RiskCalculators.CROP_BASE_RATES['default']
        )
        
        # Get risk multiplier
        risk_multiplier = RiskCalculators.get_risk_multiplier(ars_score)
        
        # Calculate base premium (percentage of coverage)
        base_premium = coverage_amount * (base_rate / 100)
        
        # Apply risk multiplier
        adjusted_premium = base_premium * risk_multiplier
        
        # Size discount (larger farms get small discount)
        if farm_size_acres >= 10:
            size_discount = 0.95
        elif farm_size_acres >= 5:
            size_discount = 0.97
        else:
            size_discount = 1.0
        
        final_premium = adjusted_premium * size_discount
        
        return (round(final_premium, 2), base_rate, risk_multiplier)
    
    @staticmethod
    def calculate_claim_validity_score(
        claim_amount: float,
        coverage_amount: float,
        policy_age_days: int,
        previous_claims_count: int,
        ai_confidence: float
    ) -> float:
        """
        Calculate claim validity score for fraud detection.
        
        Args:
            claim_amount: Claimed amount
            coverage_amount: Policy coverage amount
            policy_age_days: Days since policy issuance
            previous_claims_count: Number of previous claims
            ai_confidence: AI verification confidence (0-1)
            
        Returns:
            float: Validity score (0-1, higher = more valid)
        """
        # Claim ratio (suspicious if claiming full amount immediately)
        claim_ratio = claim_amount / coverage_amount if coverage_amount > 0 else 0
        ratio_score = 1.0 - min(1.0, claim_ratio)  # Lower ratio = higher score
        
        # Policy age (suspicious if claimed too early)
        age_score = min(1.0, policy_age_days / 30)  # Normalized to 30 days
        
        # Previous claims (more claims = potentially suspicious)
        claims_penalty = max(0, 1.0 - (previous_claims_count * 0.2))
        
        # AI verification weight
        ai_weight = ai_confidence if ai_confidence else 0.5
        
        # Weighted validity score
        validity = (
            ratio_score * 0.20 +
            age_score * 0.20 +
            claims_penalty * 0.20 +
            ai_weight * 0.40
        )
        
        return min(1.0, max(0, validity))
    
    @staticmethod
    def project_score_improvement(
        current_ars: float,
        successful_seasons: int,
        platform_days: int,
        target_months: int = 12
    ) -> Dict:
        """
        Project potential ARS improvement over time.
        
        Args:
            current_ars: Current ARS score
            successful_seasons: Successful seasons so far
            platform_days: Days active on platform
            target_months: Projection period in months
            
        Returns:
            dict: Projection data
        """
        # Improvement rate based on current score (higher scores improve faster)
        if current_ars >= 60:
            monthly_improvement = 3.0
        elif current_ars >= 40:
            monthly_improvement = 2.0
        else:
            monthly_improvement = 1.0
        
        # Additional improvement from platform engagement
        engagement_bonus = min(5.0, platform_days / 30)  # Up to 5 points bonus
        
        # Projected score
        projected_ars = max(
            0,
            current_ars - (monthly_improvement * target_months) - engagement_bonus
        )
        
        # Potential premium savings
        current_multiplier = RiskCalculators.get_risk_multiplier(current_ars)
        projected_multiplier = RiskCalculators.get_risk_multiplier(projected_ars)
        savings_percentage = ((current_multiplier - projected_multiplier) / current_multiplier * 100)
        
        return {
            'current_ars': current_ars,
            'projected_ars': projected_ars,
            'improvement_points': current_ars - projected_ars,
            'target_months': target_months,
            'current_risk_category': RiskCalculators._get_category(current_ars),
            'projected_risk_category': RiskCalculators._get_category(projected_ars),
            'potential_premium_savings_percent': max(0, savings_percentage)
        }
    
    @staticmethod
    def _get_category(ars_score: float) -> str:
        """Get risk category from ARS score."""
        if ars_score <= 20:
            return 'EXCELLENT'
        elif ars_score <= 40:
            return 'GOOD'
        elif ars_score <= 60:
            return 'MODERATE'
        elif ars_score <= 80:
            return 'HIGH'
        else:
            return 'CRITICAL'
