from flask import Blueprint, request, jsonify
from backend.services.loan_scheduler import LoanScheduler
from backend.models.loan_v2 import RepaymentSchedule, PaymentHistory, DefaultRiskScore
from backend.models.loan_request import LoanRequest
from auth_utils import token_required

loan_repayment_bp = Blueprint('loan_repayment', __name__)

@loan_repayment_bp.route('/schedule/<int:loan_id>', methods=['GET'])
@token_required
def get_schedule(current_user, loan_id):
    """Retrieves complete EMI schedule for a loan."""
    schedules = RepaymentSchedule.query.filter_by(loan_request_id=loan_id).order_by(RepaymentSchedule.installment_number).all()
    return jsonify({
        'status': 'success',
        'data': [s.to_dict() for s in schedules]
    }), 200

@loan_repayment_bp.route('/schedule/generate', methods=['POST'])
@token_required
def generate_schedule(current_user):
    """Generates EMI schedule for an approved loan."""
    data = request.get_json()
    schedules, error = LoanScheduler.generate_emi_schedule(
        loan_id=data['loan_id'],
        principal=float(data['principal']),
        annual_rate=float(data['rate']),
        tenure_months=int(data['tenure'])
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
    
    return jsonify({
        'status': 'success',
        'message': f'{len(schedules)} installments generated'
    }), 201

@loan_repayment_bp.route('/pay', methods=['POST'])
@token_required
def make_payment(current_user):
    """Records a payment against a specific installment."""
    data = request.get_json()
    payment, error = LoanScheduler.record_payment(
        loan_id=data['loan_id'],
        schedule_id=data['schedule_id'],
        amount=float(data['amount']),
        payment_method=data.get('method', 'UPI')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
    
    return jsonify({
        'status': 'success',
        'data': payment.to_dict()
    }), 201

@loan_repayment_bp.route('/history/<int:loan_id>', methods=['GET'])
@token_required
def payment_history(current_user, loan_id):
    """Retrieves payment history for a loan."""
    payments = PaymentHistory.query.filter_by(loan_request_id=loan_id).order_by(PaymentHistory.payment_date.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [p.to_dict() for p in payments]
    }), 200

@loan_repayment_bp.route('/risk/<int:loan_id>', methods=['GET'])
@token_required
def get_risk_score(current_user, loan_id):
    """Retrieves latest default risk score."""
    risk = DefaultRiskScore.query.filter_by(loan_request_id=loan_id).order_by(DefaultRiskScore.calculated_at.desc()).first()
    if not risk:
        return jsonify({'status': 'error', 'message': 'No risk assessment available'}), 404
    
    return jsonify({
        'status': 'success',
        'data': risk.to_dict()
    }), 200
