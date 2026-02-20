from flask import Blueprint, request, jsonify
from backend.services.payroll_service import PayrollService
from backend.models.labor import WorkerProfile, PayrollEntry
from auth_utils import token_required
from datetime import datetime

labor_bp = Blueprint('labor_management', __name__)

@labor_bp.route('/workers', methods=['GET'])
@token_required
def list_workers(current_user):
    farm_id = request.args.get('farm_id')
    workers = WorkerProfile.query.filter_by(farm_id=farm_id).all()
    return jsonify({
        'status': 'success',
        'data': [w.to_dict() for w in workers]
    }), 200

@labor_bp.route('/clock-in', methods=['POST'])
@token_required
def clock_in(current_user):
    data = request.get_json()
    shift, error = PayrollService.clock_in(data['worker_id'])
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
    return jsonify({'status': 'success', 'message': 'Clocked in successfully'}), 201

@labor_bp.route('/clock-out', methods=['POST'])
@token_required
def clock_out(current_user):
    data = request.get_json()
    shift, error = PayrollService.clock_out(data['worker_id'], data.get('break_mins', 0))
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
    return jsonify({'status': 'success', 'data': {'hours': shift.total_hours}}), 200

@labor_bp.route('/harvest', methods=['POST'])
@token_required
def log_harvest(current_user):
    data = request.get_json()
    log = PayrollService.log_harvest(data['worker_id'], data['crop'], data['quantity'])
    return jsonify({'status': 'success', 'message': 'Harvest logged'}), 201

@labor_bp.route('/payroll/generate', methods=['POST'])
@token_required
def generate_payroll(current_user):
    data = request.get_json()
    start = datetime.fromisoformat(data['start_date'])
    end = datetime.fromisoformat(data['end_date'])
    
    payroll, error = PayrollService.generate_worker_payroll(data['worker_id'], start, end)
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': payroll.to_dict()
    }), 201

@labor_bp.route('/payroll/history/<int:worker_id>', methods=['GET'])
@token_required
def payroll_history(current_user, worker_id):
    payrolls = PayrollEntry.query.filter_by(worker_id=worker_id).order_by(PayrollEntry.period_end.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [p.to_dict() for p in payrolls]
    }), 200
