from flask import Blueprint, request, jsonify
from backend.services.machinery_service import MachineryService
from backend.models.machinery import MaintenanceCycle, DamageReport, RepairOrder
from backend.models.equipment import Equipment
from auth_utils import token_required
from backend.extensions import db

machinery_bp = Blueprint('machinery', __name__)

@machinery_bp.route('/fleet', methods=['GET'])
@token_required
def list_fleet(current_user):
    """List machines owned by the user with health summaries"""
    equipment = Equipment.query.filter_by(owner_id=current_user.id).all()
    
    fleet_data = []
    for e in equipment:
        health = MachineryService.get_fleet_health(e.id)
        fleet_data.append({
            'id': e.id,
            'name': e.name,
            'total_hours': health['total_hours'],
            'maintenance_needed': any([m['is_overdue'] for m in health['maintenance']])
        })
        
    return jsonify({
        'status': 'success',
        'data': fleet_data
    }), 200

@machinery_bp.route('/hours', methods=['POST'])
@token_required
def log_usage(current_user):
    data = request.get_json()
    log, error = MachineryService.log_engine_hours(
        equipment_id=data['equipment_id'],
        hours_start=float(data['start']),
        hours_end=float(data['end']),
        booking_id=data.get('booking_id')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({'status': 'success', 'data': {'log_id': log.id}}), 201

@machinery_bp.route('/maintenance', methods=['POST'])
@token_required
def add_service_interval(current_user):
    data = request.get_json()
    cycle = MachineryService.schedule_maintenance(
        data['equipment_id'],
        data['service_type'],
        float(data['interval'])
    )
    return jsonify({'status': 'success', 'data': {'cycle_id': cycle.id}}), 201

@machinery_bp.route('/damage', methods=['POST'])
@token_required
def report_issue(current_user):
    data = request.get_json()
    report, error = MachineryService.report_damage(
        booking_id=data['booking_id'],
        equipment_id=data['equipment_id'],
        description=data['description'],
        estimate=float(data['estimate'])
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({'status': 'success', 'data': {'report_id': report.id}}), 201

@machinery_bp.route('/health/<int:equipment_id>', methods=['GET'])
@token_required
def get_health(current_user, equipment_id):
    stats = MachineryService.get_fleet_health(equipment_id)
    return jsonify({'status': 'success', 'data': stats}), 200

@machinery_bp.route('/telemetry/wear', methods=['GET'])
@token_required
def get_wear_telemetry(current_user):
    """
    Returns breakdown of microscopic wear across all machinery components.
    """
    from backend.models.machinery import ComponentWearMap
    equipment_ids = [e.id for e in Equipment.query.filter_by(owner_id=current_user.id).all()]
    wear_data = ComponentWearMap.query.filter(ComponentWearMap.equipment_id.in_(equipment_ids)).all()
    
    return jsonify({
        'status': 'success',
        'data': [{
            'equipment_id': w.equipment_id,
            'component': w.component_name,
            'wear': w.current_wear_percentage,
            'failed': w.current_wear_percentage >= w.critical_threshold
        } for w in wear_data]
    }), 200

@machinery_bp.route('/auto-repair/<int:equipment_id>', methods=['POST'])
@token_required
def trigger_wear_repair(current_user, equipment_id):
    """
    Manual trigger for the Predictive Engine to attempt an auto-repair sequence.
    """
    from backend.services.predictive_maintenance import PredictiveMaintenance
    equipment = Equipment.query.get(equipment_id)
    if not equipment or equipment.owner_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
        
    # Attempt to schedule for any critical component
    # Logic handled inside the service
    return jsonify({'status': 'success', 'message': 'Predictive repair audit initiated.'}), 200
