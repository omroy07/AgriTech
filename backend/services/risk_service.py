"""
Risk scoring service for Agri-Risk Score (ARS) calculation and management.
Integrates weather data, crop history, and platform activity to assess farmer risk.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_

from backend.models import (
    db, User, RiskScoreHistory, InsurancePolicy, ClaimRequest
)
from backend.utils.risk_calculators import RiskCalculators


class RiskService:
    """Service for calculating and managing agricultural risk scores."""
    
    @staticmethod
    def calculate_user_risk_score(user_id: int, force_recalculate: bool = False) -> Dict:
        """
        Calculate comprehensive Agri-Risk Score (ARS) for a user.
        
        Args:
            user_id: User ID
            force_recalculate: Force recalculation even if recent score exists
            
        Returns:
            dict: Risk score data with breakdown
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check for recent score (within 24 hours) unless force recalculate
        if not force_recalculate:
            recent_score = RiskScoreHistory.query.filter(
                and_(
                    RiskScoreHistory.user_id == user_id,
                    RiskScoreHistory.calculated_at >= datetime.utcnow() - timedelta(hours=24)
                )
            ).order_by(RiskScoreHistory.calculated_at.desc()).first()
            
            if recent_score:
                return {
                    'ars_score': recent_score.ars_score,
                    'risk_category': recent_score.risk_category,
                    'weather_risk_factor': recent_score.weather_risk_factor,
                    'crop_success_factor': recent_score.crop_success_factor,
                    'location_risk_factor': recent_score.location_risk_factor,
                    'activity_score_factor': recent_score.activity_score_factor,
                    'calculated_at': recent_score.calculated_at.isoformat(),
                    'cached': True
                }
        
        # Calculate individual risk factors
        weather_risk = RiskService._get_weather_risk(user)
        crop_success = RiskService._get_crop_success_rate(user)
        location_risk = RiskService._get_location_risk(user)
        activity_score = RiskService._get_activity_score(user)
        
        # Calculate ARS score
        ars_score = RiskCalculators.calculate_ars_score(
            weather_risk=weather_risk,
            crop_success_rate=crop_success,
            location_risk=location_risk,
            activity_score=activity_score
        )
        
        # Determine risk category
        risk_category = RiskCalculators._get_category(ars_score)
        
        # Save to history
        score_record = RiskScoreHistory(
            user_id=user_id,
            ars_score=ars_score,
            risk_category=risk_category,
            weather_risk_factor=weather_risk,
            crop_success_factor=crop_success,
            location_risk_factor=location_risk,
            activity_score_factor=activity_score
        )
        db.session.add(score_record)
        db.session.commit()
        
        return {
            'ars_score': ars_score,
            'risk_category': risk_category,
            'weather_risk_factor': weather_risk,
            'crop_success_factor': crop_success,
            'location_risk_factor': location_risk,
            'activity_score_factor': activity_score,
            'calculated_at': score_record.calculated_at.isoformat(),
            'cached': False
        }
    
    @staticmethod
    def _get_weather_risk(user: User) -> float:
        """Calculate weather risk for user's location."""
        # TODO: Integrate with weather API (OpenWeatherMap, IMD, etc.)
        # For now, using placeholder logic based on user data
        
        # Simulate weather data retrieval
        # In production, this would call weather service APIs
        rainfall_deviation = 15.0  # Placeholder: % deviation from normal
        temperature_extremes = 8  # Placeholder: extreme days count
        drought_days = 10  # Placeholder
        flood_incidents = 1  # Placeholder
        
        # Check if user has historical crop data indicating weather issues
        # This could be inferred from crop success rates
        
        return RiskCalculators.calculate_weather_risk(
            rainfall_deviation=rainfall_deviation,
            temperature_extremes=temperature_extremes,
            drought_days=drought_days,
            flood_incidents=flood_incidents
        )
    
    @staticmethod
    def _get_crop_success_rate(user: User) -> float:
        """Calculate crop success rate from user's history."""
        # TODO: Query actual crop yield data from CropCalendar or similar
        # For now, using placeholder based on user tenure
        
        # Simulate crop history
        # In production, query from crop_yields table
        user_age_days = (datetime.utcnow() - user.created_at).days
        
        if user_age_days < 90:
            # New farmer - neutral score
            successful_seasons = 0
            total_seasons = 0
            avg_yield = 50.0
        elif user_age_days < 180:
            successful_seasons = 1
            total_seasons = 1
            avg_yield = 70.0
        else:
            # Estimate based on user activity
            successful_seasons = max(1, user_age_days // 120)
            total_seasons = max(2, user_age_days // 90)
            avg_yield = 75.0
        
        return RiskCalculators.calculate_crop_success_rate(
            successful_seasons=successful_seasons,
            total_seasons=total_seasons,
            avg_yield_percentage=avg_yield
        )
    
    @staticmethod
    def _get_location_risk(user: User) -> float:
        """Calculate location-based risk."""
        # TODO: Use actual location data from user profile
        # Integrate with disaster database, soil quality data
        
        district = "general_area"  # Placeholder
        historical_disasters = 3  # Placeholder
        soil_quality = 0.6  # Placeholder (0-1 scale)
        has_irrigation = True  # Placeholder
        
        return RiskCalculators.calculate_location_risk(
            district=district,
            historical_disaster_count=historical_disasters,
            soil_quality_index=soil_quality,
            irrigation_access=has_irrigation
        )
    
    @staticmethod
    def _get_activity_score(user: User) -> float:
        """Calculate platform activity/engagement score."""
        days_active = (datetime.utcnow() - user.created_at).days
        
        # Count user interactions (placeholder - would query actual activities)
        # TODO: Query marketplace transactions, forum posts, etc.
        transactions_count = 5  # Placeholder
        
        # Data completeness (check profile fields)
        completeness = 0.7  # Placeholder - calculate from actual profile
        
        return RiskCalculators.calculate_activity_score(
            days_active=days_active,
            transactions_count=transactions_count,
            data_completeness=completeness
        )
    
    @staticmethod
    def get_score_history(user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get historical risk scores for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            
        Returns:
            list: Score history records
        """
        records = RiskScoreHistory.query.filter_by(user_id=user_id)\
            .order_by(RiskScoreHistory.calculated_at.desc())\
            .limit(limit)\
            .all()
        
        return [record.to_dict() for record in records]
    
    @staticmethod
    def get_score_trend(user_id: int, days: int = 90) -> Dict:
        """
        Analyze risk score trend over time.
        
        Args:
            user_id: User ID
            days: Period to analyze
            
        Returns:
            dict: Trend analysis
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        records = RiskScoreHistory.query.filter(
            and_(
                RiskScoreHistory.user_id == user_id,
                RiskScoreHistory.calculated_at >= cutoff_date
            )
        ).order_by(RiskScoreHistory.calculated_at.asc()).all()
        
        if not records:
            return {
                'trend': 'no_data',
                'records_count': 0,
                'improvement': 0
            }
        
        first_score = records[0].ars_score
        last_score = records[-1].ars_score
        improvement = first_score - last_score  # Lower ARS is better
        
        if improvement > 5:
            trend = 'improving'
        elif improvement < -5:
            trend = 'worsening'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'records_count': len(records),
            'improvement': improvement,
            'first_score': first_score,
            'last_score': last_score,
            'first_date': records[0].calculated_at.isoformat(),
            'last_date': records[-1].calculated_at.isoformat()
        }
    
    @staticmethod
    def get_improvement_suggestions(user_id: int) -> Dict:
        """
        Get personalized suggestions to improve ARS score.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Improvement suggestions
        """
        # Get latest score
        latest_score = RiskScoreHistory.query.filter_by(user_id=user_id)\
            .order_by(RiskScoreHistory.calculated_at.desc())\
            .first()
        
        if not latest_score:
            return {
                'message': 'No risk score available. Complete your profile to get a score.',
                'suggestions': []
            }
        
        suggestions = []
        
        # Analyze each risk factor
        if latest_score.weather_risk_factor > 0.6:
            suggestions.append({
                'category': 'weather_risk',
                'severity': 'high',
                'suggestion': 'Consider weather-resistant crop varieties or rainwater harvesting',
                'impact': 'Could reduce weather risk factor by 20-30%'
            })
        
        if latest_score.crop_success_factor < 0.6:
            suggestions.append({
                'category': 'crop_success',
                'severity': 'medium',
                'suggestion': 'Track crop yields regularly and use soil testing services',
                'impact': 'Improved documentation can boost success factor'
            })
        
        if latest_score.location_risk_factor > 0.7:
            suggestions.append({
                'category': 'location_risk',
                'severity': 'high',
                'suggestion': 'Invest in irrigation infrastructure or crop insurance for high-risk areas',
                'impact': 'Can offset location risk impact on premiums'
            })
        
        if latest_score.activity_score_factor < 0.5:
            suggestions.append({
                'category': 'platform_activity',
                'severity': 'low',
                'suggestion': 'Complete your profile and participate in community forums',
                'impact': 'Better engagement can reduce premiums by 5-10%'
            })
        
        # Calculate projection
        user = User.query.get(user_id)
        days_active = (datetime.utcnow() - user.created_at).days
        
        projection = RiskCalculators.project_score_improvement(
            current_ars=latest_score.ars_score,
            successful_seasons=1,  # Placeholder
            platform_days=days_active,
            target_months=12
        )
        
        return {
            'current_score': latest_score.ars_score,
            'current_category': latest_score.risk_category,
            'suggestions': suggestions,
            'projection': projection
        }
    
    @staticmethod
    def calculate_premium_estimate(
        user_id: int,
        coverage_amount: float,
        crop_type: str,
        farm_size: float
    ) -> Dict:
        """
        Calculate insurance premium estimate based on user's ARS.
        
        Args:
            user_id: User ID
            coverage_amount: Desired coverage
            crop_type: Crop type
            farm_size: Farm size in acres
            
        Returns:
            dict: Premium breakdown
        """
        # Get current risk score
        score_data = RiskService.calculate_user_risk_score(user_id)
        ars_score = score_data['ars_score']
        
        # Calculate premium
        premium, base_rate, risk_multiplier = RiskCalculators.calculate_premium(
            coverage_amount=coverage_amount,
            crop_type=crop_type,
            ars_score=ars_score,
            farm_size_acres=farm_size
        )
        
        return {
            'premium_amount': premium,
            'coverage_amount': coverage_amount,
            'base_rate_percentage': base_rate,
            'risk_multiplier': risk_multiplier,
            'ars_score': ars_score,
            'risk_category': score_data['risk_category'],
            'crop_type': crop_type,
            'farm_size_acres': farm_size
        }
