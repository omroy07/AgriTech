"""
Risk scoring API endpoints for Agri-Risk Score (ARS) management.
"""

from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate, ValidationError

from backend.services.risk_service import RiskService
from backend.auth_utils import token_required


risk_bp = Blueprint('risk', __name__, url_prefix='/api/v1/risk')


# ===== Validation Schemas =====

class PremiumEstimateSchema(Schema):
    """Schema for premium estimation."""
    coverage_amount = fields.Float(required=True, validate=validate.Range(min=10000))
    crop_type = fields.Str(required=True)
    farm_size = fields.Float(required=True, validate=validate.Range(min=0.1))


# ===== Risk Score Endpoints =====

@risk_bp.route('/score', methods=['GET'])
@token_required
def get_risk_score(current_user):
    """
    Get current Agri-Risk Score (ARS) for the user.
    
    Query Parameters:
    - force_recalculate: true/false (default: false)
    
    Returns:
    {
        "ars_score": 45.2,
        "risk_category": "MODERATE",
        "weather_risk_factor": 0.35,
        "crop_success_factor": 0.65,
        "location_risk_factor": 0.40,
        "activity_score_factor": 0.70,
        "calculated_at": "2024-01-20T10:30:00Z",
        "cached": false
    }
    """
    try:
        force_recalc = request.args.get('force_recalculate', 'false').lower() == 'true'
        
        score_data = RiskService.calculate_user_risk_score(
            user_id=current_user.id,
            force_recalculate=force_recalc
        )
        
        return jsonify({
            'success': True,
            'data': score_data
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to calculate risk score',
            'details': str(e)
        }), 500


@risk_bp.route('/score/calculate', methods=['POST'])
@token_required
def trigger_score_calculation(current_user):
    """
    Trigger a fresh ARS calculation.
    Same as GET /score?force_recalculate=true
    """
    try:
        score_data = RiskService.calculate_user_risk_score(
            user_id=current_user.id,
            force_recalculate=True
        )
        
        return jsonify({
            'success': True,
            'data': score_data,
            'message': 'Risk score calculated successfully'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to calculate risk score',
            'details': str(e)
        }), 500


@risk_bp.route('/history', methods=['GET'])
@token_required
def get_score_history(current_user):
    """
    Get historical risk scores.
    
    Query Parameters:
    - limit: Number of records (default: 10)
    
    Returns:
    [
        {
            "ars_score": 45.2,
            "risk_category": "MODERATE",
            "calculated_at": "2024-01-20T10:30:00Z",
            ...
        }
    ]
    """
    try:
        limit = int(request.args.get('limit', 10))
        limit = min(max(1, limit), 100)  # Clamp between 1-100
        
        history = RiskService.get_score_history(
            user_id=current_user.id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': history,
            'count': len(history)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch score history',
            'details': str(e)
        }), 500


@risk_bp.route('/trend', methods=['GET'])
@token_required
def get_score_trend(current_user):
    """
    Analyze risk score trend over time.
    
    Query Parameters:
    - days: Analysis period (default: 90)
    
    Returns:
    {
        "trend": "improving",  // improving, worsening, stable
        "records_count": 5,
        "improvement": 12.5,
        "first_score": 57.7,
        "last_score": 45.2,
        "first_date": "2023-11-01T10:00:00Z",
        "last_date": "2024-01-20T10:30:00Z"
    }
    """
    try:
        days = int(request.args.get('days', 90))
        days = min(max(7, days), 365)  # Clamp between 7-365
        
        trend = RiskService.get_score_trend(
            user_id=current_user.id,
            days=days
        )
        
        return jsonify({
            'success': True,
            'data': trend
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to analyze trend',
            'details': str(e)
        }), 500


@risk_bp.route('/insights', methods=['GET'])
@token_required
def get_improvement_insights(current_user):
    """
    Get personalized suggestions to improve ARS score.
    
    Returns:
    {
        "current_score": 45.2,
        "current_category": "MODERATE",
        "suggestions": [
            {
                "category": "weather_risk",
                "severity": "high",
                "suggestion": "Consider weather-resistant crop varieties...",
                "impact": "Could reduce weather risk factor by 20-30%"
            }
        ],
        "projection": {
            "current_ars": 45.2,
            "projected_ars": 32.1,
            "improvement_points": 13.1,
            "target_months": 12,
            "current_risk_category": "MODERATE",
            "projected_risk_category": "GOOD",
            "potential_premium_savings_percent": 18.5
        }
    }
    """
    try:
        insights = RiskService.get_improvement_suggestions(user_id=current_user.id)
        
        return jsonify({
            'success': True,
            'data': insights
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get insights',
            'details': str(e)
        }), 500


@risk_bp.route('/premium/estimate', methods=['POST'])
@token_required
def estimate_premium(current_user):
    """
    Calculate insurance premium estimate based on current ARS.
    
    Request Body:
    {
        "coverage_amount": 100000,
        "crop_type": "rice",
        "farm_size": 5.0
    }
    
    Returns:
    {
        "premium_amount": 3500.00,
        "coverage_amount": 100000,
        "base_rate_percentage": 3.5,
        "risk_multiplier": 1.0,
        "ars_score": 45.2,
        "risk_category": "MODERATE",
        "crop_type": "rice",
        "farm_size_acres": 5.0
    }
    """
    try:
        schema = PremiumEstimateSchema()
        data = schema.load(request.json)
        
        estimate = RiskService.calculate_premium_estimate(
            user_id=current_user.id,
            coverage_amount=data['coverage_amount'],
            crop_type=data['crop_type'],
            farm_size=data['farm_size']
        )
        
        return jsonify({
            'success': True,
            'data': estimate
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': e.messages
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to estimate premium',
            'details': str(e)
        }), 500


@risk_bp.route('/categories', methods=['GET'])
def get_risk_categories():
    """
    Get risk category definitions (public endpoint).
    
    Returns:
    [
        {
            "category": "EXCELLENT",
            "score_range": "0-20",
            "description": "Lowest risk profile",
            "risk_multiplier": 0.7,
            "premium_impact": "30% discount"
        },
        ...
    ]
    """
    categories = [
        {
            'category': 'EXCELLENT',
            'score_range': '0-20',
            'description': 'Lowest risk profile with excellent farming practices',
            'risk_multiplier': 0.7,
            'premium_impact': '30% discount'
        },
        {
            'category': 'GOOD',
            'score_range': '21-40',
            'description': 'Low risk with good track record',
            'risk_multiplier': 0.9,
            'premium_impact': '10% discount'
        },
        {
            'category': 'MODERATE',
            'score_range': '41-60',
            'description': 'Average risk profile',
            'risk_multiplier': 1.0,
            'premium_impact': 'Standard rates'
        },
        {
            'category': 'HIGH',
            'score_range': '61-80',
            'description': 'Higher risk requiring attention',
            'risk_multiplier': 1.3,
            'premium_impact': '30% increase'
        },
        {
            'category': 'CRITICAL',
            'score_range': '81-100',
            'description': 'Highest risk category',
            'risk_multiplier': 1.6,
            'premium_impact': '60% increase'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': categories
    })


@risk_bp.route('/factors', methods=['GET'])
def get_risk_factors():
    """
    Get information about risk factors (public endpoint).
    
    Returns:
    [
        {
            "factor": "weather_risk",
            "weight": 0.35,
            "description": "Weather patterns and climate conditions",
            "components": ["Rainfall deviation", "Temperature extremes", ...]
        },
        ...
    ]
    """
    factors = [
        {
            'factor': 'weather_risk',
            'weight': 0.35,
            'description': 'Weather patterns and climate conditions affecting crops',
            'components': [
                'Rainfall deviation from normal',
                'Temperature extremes',
                'Drought days',
                'Flood incidents'
            ],
            'improvement_tips': [
                'Use weather-resistant crop varieties',
                'Implement rainwater harvesting',
                'Install irrigation systems'
            ]
        },
        {
            'factor': 'crop_success',
            'weight': 0.30,
            'description': 'Historical crop yield and success rates',
            'components': [
                'Successful seasons count',
                'Total seasons farmed',
                'Average yield percentage'
            ],
            'improvement_tips': [
                'Document all crop cycles',
                'Use soil testing services',
                'Follow recommended farming practices'
            ]
        },
        {
            'factor': 'location_risk',
            'weight': 0.25,
            'description': 'Geographic and environmental risk factors',
            'components': [
                'District disaster history',
                'Soil quality index',
                'Irrigation access'
            ],
            'improvement_tips': [
                'Improve soil quality',
                'Invest in irrigation',
                'Use appropriate crops for location'
            ]
        },
        {
            'factor': 'platform_activity',
            'weight': 0.10,
            'description': 'Engagement and data quality on platform',
            'components': [
                'Days active',
                'Transaction count',
                'Profile completeness'
            ],
            'improvement_tips': [
                'Complete your profile',
                'Regular platform engagement',
                'Document farming activities'
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'data': factors
    })


# ===== Health Check =====

@risk_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'service': 'risk_scoring',
        'status': 'operational'
    })
