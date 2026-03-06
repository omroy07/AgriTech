from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.precision_irrigation import WaterStressIndex, IrrigationValveAutomation, AquiferMonitoring
from backend.services.irrigation_orchestrator import IrrigationOrchestrator
from backend.extensions import db

irrigation_v2_bp = Blueprint('irrigation_v2', __name__)

@irrigation_v2_bp.route('/stress/logs', methods=['GET'])
@token_required
def get_stress_logs(current_user):
    """Retrieve historical water stress data."""
    farm_id = request.args.get('farm_id')
    logs = WaterStressIndex.query.filter_by(farm_id=farm_id).order_by(WaterStressIndex.recorded_at.desc()).limit(50).all()
    return jsonify({
        'status': 'success',
        'data': [l.to_dict() for l in logs]
    }), 200

@irrigation_v2_bp.route('/valves/status', methods=['GET'])
@token_required
def get_valve_states(current_user):
    """View the current status of all smart valves on a farm."""
    farm_id = request.args.get('farm_id')
    valves = IrrigationValveAutomation.query.filter_by(farm_id=farm_id).all()
    return jsonify({
        'status': 'success',
        'data': [v.to_dict() for v in valves]
    }), 200

@irrigation_v2_bp.route('/aquifer/health', methods=['GET'])
@token_required
def get_aquifer_health(current_user):
    """Monitor regional aquifer water levels and depletion risks."""
    aquifer_id = request.args.get('aquifer_id')
    latest = AquiferMonitoring.query.filter_by(aquifer_id=aquifer_id).order_by(AquiferMonitoring.recorded_at.desc()).first()
    
    if not latest:
        return jsonify({'error': 'No data found for this aquifer'}), 404
        
    return jsonify({
        'status': 'success',
        'data': {
            'level': latest.current_water_level_m,
            'recharge_rate': latest.recharge_rate_lps,
            'is_critical': latest.is_critical_depletion
        }
    }), 200
