from flask import Blueprint, jsonify, request
from backend.services.maintenance_logic import MaintenanceLogic
from backend.models.equipment import Equipment
from backend.models.reliability_log import ReliabilityLog
from backend.services.audit_service import AuditService
from backend.auth_utils import token_required
from backend.extensions import db

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/<int:equipment_id>/audit', methods=['POST'])
@token_required
def manual_audit(current_user, equipment_id):
    """
    Trigger immediate reliability re-calculation for specific machinery.
    Useful for 'Start of Shift' checks.
    """
    equip = Equipment.query.get(equipment_id)
    if not equip:
        return jsonify({'status': 'error', 'message': 'Equipment not found'}), 404
        
    score = MaintenanceLogic.update_reliability_score(equipment_id)
    
    return jsonify({
        'status': 'success',
        'reliability_score': score,
        'safe_to_operate': equip.is_safe_to_operate()
    })

@maintenance_bp.route('/<int:equipment_id>/skill-check', methods=['POST'])
@token_required
def check_operator(current_user, equipment_id):
    """
    Validates if the current user (Or assigned worker) has necessary certification.
    """
    data = request.get_json()
    worker_id = data.get('worker_id', current_user.id)
    
    equip = Equipment.query.get(equipment_id)
    if not equip:
        return jsonify({'status': 'error'}), 404
        
    valid, level = MaintenanceLogic.validate_operator_skill(worker_id, equip.category)
    
    return jsonify({
        'status': 'success' if valid else 'error',
        'is_certified': valid,
        'level': level
    })

@maintenance_bp.route('/reliability-report/<int:equipment_id>', methods=['GET'])
@token_required
def get_report(current_user, equipment_id):
    """Deep telemetry reporting for Fleet Dashboard"""
    equip = Equipment.query.get(equipment_id)
    logs = ReliabilityLog.query.filter_by(equipment_id=equipment_id).order_by(ReliabilityLog.recorded_at.desc()).limit(20).all()
    
    history = [{
        'time': l.recorded_at.isoformat(),
        'score': l.calculated_reliability_score,
        'trigger': l.trigger_event
    } for l in logs]
    
    return jsonify({
        'status': 'success',
        'metrics': {
            'vibration': equip.vibration_level,
            'heat': equip.heat_index,
            'current_score': equip.reliability_score,
            'duty_cycle': equip.duty_cycle_rating
        },
        'history': history
    })
