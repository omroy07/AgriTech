"""
Insurance API endpoints for policy management and claims.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from marshmallow import Schema, fields, validate, ValidationError

from backend.services.insurance_service import InsuranceService
from backend.services.audit_service import AuditService
from backend.auth_utils import token_required


insurance_bp = Blueprint('insurance', __name__, url_prefix='/api/v1/insurance')


# ===== Validation Schemas =====

class CreatePolicySchema(Schema):
    """Schema for policy creation."""
    coverage_amount = fields.Float(required=True, validate=validate.Range(min=10000))
    crop_type = fields.Str(required=True)
    farm_location = fields.Str(required=True)
    farm_size = fields.Float(required=True, validate=validate.Range(min=0.1))
    coverage_months = fields.Int(missing=6, validate=validate.Range(min=3, max=12))


class SubmitClaimSchema(Schema):
    """Schema for claim submission."""
    policy_id = fields.Int(required=True)
    claimed_amount = fields.Float(required=True, validate=validate.Range(min=1))
    incident_date = fields.DateTime(required=True)
    incident_description = fields.Str(required=True, validate=validate.Length(min=20))
    evidence_photos = fields.List(fields.Str(), missing=[])


class ProcessClaimSchema(Schema):
    """Schema for claim processing (admin)."""
    decision = fields.Str(required=True, validate=validate.OneOf(['APPROVED', 'REJECTED']))
    approved_amount = fields.Float()
    rejection_reason = fields.Str()


class RenewPolicySchema(Schema):
    """Schema for policy renewal."""
    coverage_months = fields.Int(missing=6, validate=validate.Range(min=3, max=12))
    adjust_coverage = fields.Float(validate=validate.Range(min=10000))


# ===== Policy Endpoints =====

@insurance_bp.route('/policies', methods=['POST'])
@token_required
def create_policy(current_user):
    """
    Create a new insurance policy.
    
    Request Body:
    {
        "coverage_amount": 100000,
        "crop_type": "rice",
        "farm_location": "Village ABC, District XYZ",
        "farm_size": 5.0,
        "coverage_months": 6
    }
    """
    try:
        schema = CreatePolicySchema()
        data = schema.load(request.json)
        
        policy = InsuranceService.create_policy(
            user_id=current_user.id,
            coverage_amount=data['coverage_amount'],
            crop_type=data['crop_type'],
            farm_location=data['farm_location'],
            farm_size=data['farm_size'],
            coverage_months=data['coverage_months']
        )
        
        AuditService.log_action(
            action="CREATE_INSURANCE_POLICY",
            user_id=current_user.id,
            resource_type="INSURANCE_POLICY",
            resource_id=str(policy['id']),
            meta_data=data
        )
        
        return jsonify({
            'success': True,
            'data': policy
        }), 201
        
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
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create policy',
            'details': str(e)
        }), 500


@insurance_bp.route('/policies', methods=['GET'])
@token_required
def get_policies(current_user):
    """
    Get all policies for current user.
    
    Query Parameters:
    - status: Filter by status (ACTIVE, EXPIRED, CANCELLED, CLAIMED)
    - active_only: true/false
    """
    try:
        status = request.args.get('status')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        policies = InsuranceService.get_user_policies(
            user_id=current_user.id,
            status=status,
            active_only=active_only
        )
        
        return jsonify({
            'success': True,
            'data': policies,
            'count': len(policies)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch policies',
            'details': str(e)
        }), 500


@insurance_bp.route('/policies/<int:policy_id>', methods=['GET'])
@token_required
def get_policy_details(current_user, policy_id):
    """Get detailed information about a specific policy."""
    try:
        policy = InsuranceService.get_policy_details(policy_id)
        
        # Verify ownership
        if policy['user_id'] != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to policy'
            }), 403
        
        return jsonify({
            'success': True,
            'data': policy
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch policy',
            'details': str(e)
        }), 500


@insurance_bp.route('/policies/<int:policy_id>/renew', methods=['POST'])
@token_required
def renew_policy(current_user, policy_id):
    """
    Renew an existing policy.
    
    Request Body:
    {
        "coverage_months": 6,
        "adjust_coverage": 120000  // optional
    }
    """
    try:
        schema = RenewPolicySchema()
        data = schema.load(request.json)
        
        # Verify ownership (get policy first)
        from backend.models import InsurancePolicy
        policy = InsurancePolicy.query.get(policy_id)
        if not policy or policy.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Policy not found or unauthorized'
            }), 404
        
        renewed_policy = InsuranceService.renew_policy(
            policy_id=policy_id,
            coverage_months=data['coverage_months'],
            adjust_coverage=data.get('adjust_coverage')
        )
        
        AuditService.log_action(
            action="RENEW_INSURANCE_POLICY",
            user_id=current_user.id,
            resource_type="INSURANCE_POLICY",
            resource_id=str(policy_id),
            meta_data=data
        )
        
        return jsonify({
            'success': True,
            'data': renewed_policy
        }), 201
        
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
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to renew policy',
            'details': str(e)
        }), 500


@insurance_bp.route('/policies/<int:policy_id>/cancel', methods=['POST'])
@token_required
def cancel_policy(current_user, policy_id):
    """
    Cancel a policy.
    
    Request Body:
    {
        "reason": "No longer needed"
    }
    """
    try:
        data = request.json or {}
        reason = data.get('reason', 'User requested cancellation')
        
        # Verify ownership
        from backend.models import InsurancePolicy
        policy = InsurancePolicy.query.get(policy_id)
        if not policy or policy.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Policy not found or unauthorized'
            }), 404
        
        result = InsuranceService.cancel_policy(policy_id, reason)
        
        AuditService.log_action(
            action="CANCEL_INSURANCE_POLICY",
            user_id=current_user.id,
            resource_type="INSURANCE_POLICY",
            resource_id=str(policy_id),
            risk_level='MEDIUM',
            meta_data={"reason": reason}
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to cancel policy',
            'details': str(e)
        }), 500


# ===== Claim Endpoints =====

@insurance_bp.route('/claims', methods=['POST'])
@token_required
def submit_claim(current_user):
    """
    Submit an insurance claim.
    
    Request Body:
    {
        "policy_id": 123,
        "claimed_amount": 50000,
        "incident_date": "2024-01-15T10:00:00Z",
        "incident_description": "Crop damage due to heavy rainfall...",
        "evidence_photos": ["url1", "url2"]
    }
    """
    try:
        schema = SubmitClaimSchema()
        data = schema.load(request.json)
        
        # Verify policy ownership
        from backend.models import InsurancePolicy
        policy = InsurancePolicy.query.get(data['policy_id'])
        if not policy or policy.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Policy not found or unauthorized'
            }), 404
        
        claim = InsuranceService.submit_claim(
            policy_id=data['policy_id'],
            claimed_amount=data['claimed_amount'],
            incident_date=data['incident_date'],
            incident_description=data['incident_description'],
            evidence_photos=data['evidence_photos']
        )
        
        AuditService.log_action(
            action="SUBMIT_INSURANCE_CLAIM",
            user_id=current_user.id,
            resource_type="INSURANCE_CLAIM",
            resource_id=str(claim['id']),
            risk_level='MEDIUM',
            meta_data=data
        )
        
        return jsonify({
            'success': True,
            'data': claim
        }), 201
        
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
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to submit claim',
            'details': str(e)
        }), 500


@insurance_bp.route('/claims', methods=['GET'])
@token_required
def get_claims(current_user):
    """
    Get all claims for current user.
    
    Query Parameters:
    - status: Filter by status (SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, PAID)
    """
    try:
        status = request.args.get('status')
        
        claims = InsuranceService.get_user_claims(
            user_id=current_user.id,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': claims,
            'count': len(claims)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch claims',
            'details': str(e)
        }), 500


# ===== Statistics Endpoints =====

@insurance_bp.route('/statistics', methods=['GET'])
@token_required
def get_statistics(current_user):
    """Get insurance statistics for current user."""
    try:
        stats = InsuranceService.get_insurance_statistics(user_id=current_user.id)
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics',
            'details': str(e)
        }), 500


# ===== Admin Endpoints =====

@insurance_bp.route('/admin/claims/<int:claim_id>/process', methods=['POST'])
@token_required
def process_claim(current_user, claim_id):
    """
    Process a claim (admin only).
    
    Request Body:
    {
        "decision": "APPROVED",  // or "REJECTED"
        "approved_amount": 45000,  // if approved
        "rejection_reason": "Insufficient evidence"  // if rejected
    }
    """
    # TODO: Add admin role check
    # if current_user.role != 'admin':
    #     return jsonify({'success': False, 'error': 'Admin access required'}), 403
    
    try:
        schema = ProcessClaimSchema()
        data = schema.load(request.json)
        
        result = InsuranceService.process_claim_decision(
            claim_id=claim_id,
            decision=data['decision'],
            approved_amount=data.get('approved_amount'),
            rejection_reason=data.get('rejection_reason'),
            processed_by=current_user.id
        )
        
        AuditService.log_action(
            action="PROCESS_INSURANCE_CLAIM",
            user_id=current_user.id,
            resource_type="INSURANCE_CLAIM",
            resource_id=str(claim_id),
            risk_level='HIGH' if data['decision'] == 'APPROVED' else 'MEDIUM',
            meta_data=data
        )
        
        return jsonify({
            'success': True,
            'data': result
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
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process claim',
            'details': str(e)
        }), 500


@insurance_bp.route('/admin/claims/<int:claim_id>/pay', methods=['POST'])
@token_required
def mark_as_paid(current_user, claim_id):
    """
    Mark claim as paid (admin only).
    
    Request Body:
    {
        "payment_reference": "TXN123456"
    }
    """
    # TODO: Add admin role check
    
    try:
        data = request.json or {}
        payment_ref = data.get('payment_reference', f'PAY-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}')
        
        result = InsuranceService.mark_claim_paid(claim_id, payment_ref)
        
        AuditService.log_action(
            action="PAY_INSURANCE_CLAIM",
            user_id=current_user.id,
            resource_type="INSURANCE_CLAIM",
            resource_id=str(claim_id),
            risk_level='HIGH',
            meta_data={"payment_reference": payment_ref}
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to mark claim as paid',
            'details': str(e)
        }), 500


@insurance_bp.route('/admin/statistics', methods=['GET'])
@token_required
def get_admin_statistics(current_user):
    """Get global insurance statistics (admin only)."""
    # TODO: Add admin role check
    
    try:
        stats = InsuranceService.get_insurance_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics',
            'details': str(e)
        }), 500


# ===== Risk & Premium Audit Endpoints (L3-1557) =====

@insurance_bp.route('/policies/<int:policy_id>/risk-visibility', methods=['GET'])
@token_required
def get_risk_visibility(current_user, policy_id):
    """Returns real-time risk factors and suspension status for a policy."""
    from backend.models.insurance import InsurancePolicy, RiskFactorSnapshot

    policy = InsurancePolicy.query.get(policy_id)
    if not policy or policy.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Policy not found'}), 404

    latest_snapshot = RiskFactorSnapshot.query.filter_by(policy_id=policy_id).order_by(RiskFactorSnapshot.recorded_at.desc()).first()

    return jsonify({
        'success': True,
        'data': {
            'current_risk_score': policy.current_risk_score,
            'is_suspended': policy.is_suspended,
            'suspension_reason': policy.suspension_reason,
            'factors': {
                'weather_index': latest_snapshot.weather_risk_index if latest_snapshot else 1.0,
                'telemetry_index': latest_snapshot.telemetry_risk_index if latest_snapshot else 1.0,
                'sustainability_discount': latest_snapshot.sustainability_discount_factor if latest_snapshot else 0.0
            }
        }
    })

@insurance_bp.route('/policies/<int:policy_id>/premium-audit', methods=['GET'])
@token_required
def get_premium_audit(current_user, policy_id):
    """Returns a history of all automatic premium adjustments."""
    from backend.models.insurance import InsurancePolicy, DynamicPremiumLog

    policy = InsurancePolicy.query.get(policy_id)
    if not policy or policy.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Policy not found'}), 404

    logs = DynamicPremiumLog.query.filter_by(policy_id=policy_id).order_by(DynamicPremiumLog.timestamp.desc()).all()

    return jsonify({
        'success': True,
        'data': [
            {
                'old': float(log.old_premium),
                'new': float(log.new_premium),
                'reason': log.change_reason,
                'triggered_by': log.triggered_by,
                'timestamp': log.timestamp.isoformat()
            } for log in logs
        ]
    })

@insurance_bp.route('/recalculate-risk/<int:policy_id>', methods=['POST'])
@token_required
def manual_risk_recalc(current_user, policy_id):
    """Manual trigger for the risk orchestration engine."""
    from backend.services.risk_adjustment_service import RiskAdjustmentService

    # Audit trail for manual trigger
    from backend.services.audit_service import AuditService
    AuditService.log_event(
        user_id=current_user.id,
        action="MANUAL_RISK_RECALC",
        resource_type="POLICY",
        resource_id=policy_id,
        details="User manually triggered risk recalculation",
        risk_level="LOW"
    )

    score = RiskAdjustmentService.calculate_actuarial_flux(policy_id)
    return jsonify({
        'success': True,
        'new_risk_score': score
    })
