from flask import Blueprint, jsonify, request
from backend.services.solvency_forecaster import SolvencyForecaster
from backend.models.financials import FarmBalanceSheet, SolvencySnapshot
from backend.auth_utils import token_required
from backend.extensions import db

financials_bp = Blueprint('financials', __name__)

@financials_bp.route('/dashboard/<int:farm_id>', methods=['GET'])
@token_required
def get_financial_dashboard(current_user, farm_id):
    """
    Returns high-level financial health metrics, solvency ratios, and liquidation priorities.
    """
    balance = FarmBalanceSheet.query.filter_by(farm_id=farm_id).order_by(FarmBalanceSheet.period_date.desc()).first()
    snapshot = SolvencySnapshot.query.filter_by(farm_id=farm_id).order_by(SolvencySnapshot.created_at.desc()).first()
    
    if not snapshot:
        # Trigger fresh calculation
        snapshot = SolvencyForecaster.calculate_bankruptcy_risk(farm_id)
        
    liquidation_list = SolvencyForecaster.generate_liquidation_priority_list(farm_id)
    
    return jsonify({
        'status': 'success',
        'balance_sheet': balance.to_dict() if balance else None,
        'solvency': snapshot.to_dict(),
        'liquidation_priority': liquidation_list
    })

@financials_bp.route('/risk-audit', methods=['POST'])
@token_required
def manual_risk_audit(current_user):
    """Allows manual trigger of the solvency brain for a specific farm."""
    data = request.get_json()
    farm_id = data.get('farm_id')
    
    snapshot = SolvencyForecaster.calculate_bankruptcy_risk(farm_id)
    return jsonify({
        'status': 'success',
        'risk_score': snapshot.bankruptcy_risk_score,
        'alert_status': snapshot.status
    })

@financials_bp.route('/liquidity-projections/<int:farm_id>', methods=['GET'])
@token_required
def get_projections(current_user, farm_id):
    """
    Simulated liquidity projections based on current debt and estimated harvest value.
    """
    # Placeholder for complex predictive UI logic
    return jsonify({
        'status': 'success',
        'projections': [
            {'month': 'March', 'liquidity': 1.2},
            {'month': 'April', 'liquidity': 1.1},
            {'month': 'May', 'liquidity': 0.8, 'warning': 'Low Harvest Prediction'}
        ]
    })
