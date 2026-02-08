"""
Pool Contributions API Endpoints
"""

from flask import Blueprint, request, jsonify
from backend.models import PoolContribution, YieldPool
from backend.services.pool_service import PoolService
from backend.services.financial_service import FinancialService
import logging

logger = logging.getLogger(__name__)

contributions_bp = Blueprint('contributions', __name__, url_prefix='/api/v1/contributions')


@contributions_bp.route('', methods=['POST'])
def add_contribution():
    """Add a contribution to a pool."""
    try:
        data = request.get_json()
        
        pool_id = data.get('pool_id')
        user_id = data.get('user_id', 1)  # TODO: Get from JWT
        quantity_tons = data.get('quantity_tons')
        quality_grade = data.get('quality_grade', 'A')
        
        if not pool_id or not quantity_tons:
            return jsonify({'error': 'pool_id and quantity_tons are required'}), 400
        
        if quantity_tons <= 0:
            return jsonify({'error': 'quantity_tons must be positive'}), 400
        
        contribution, error = PoolService.add_contribution(
            pool_id, user_id, quantity_tons, quality_grade
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'contribution': contribution.to_dict(),
            'message': 'Contribution added successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to add contribution: {str(e)}")
        return jsonify({'error': 'Failed to add contribution'}), 500


@contributions_bp.route('/pool/<int:pool_id>', methods=['GET'])
def get_pool_contributions(pool_id):
    """Get all contributions for a specific pool."""
    try:
        contributions = PoolContribution.query.filter_by(pool_id=pool_id).all()
        
        return jsonify({
            'success': True,
            'pool_id': pool_id,
            'count': len(contributions),
            'contributions': [c.to_dict() for c in contributions]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get contributions: {str(e)}")
        return jsonify({'error': 'Failed to get contributions'}), 500


@contributions_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_contributions(user_id):
    """Get all contributions by a specific user."""
    try:
        contributions = PoolContribution.query.filter_by(user_id=user_id).all()
        
        # Include pool details
        result = []
        for contribution in contributions:
            contrib_dict = contribution.to_dict()
            if contribution.pool:
                contrib_dict['pool'] = {
                    'pool_id': contribution.pool.pool_id,
                    'pool_name': contribution.pool.pool_name,
                    'crop_type': contribution.pool.crop_type,
                    'status': contribution.pool.status
                }
            result.append(contrib_dict)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'count': len(contributions),
            'contributions': result
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get user contributions: {str(e)}")
        return jsonify({'error': 'Failed to get contributions'}), 500


@contributions_bp.route('/<int:contribution_id>', methods=['GET'])
def get_contribution(contribution_id):
    """Get details of a specific contribution."""
    try:
        contribution = PoolContribution.query.get(contribution_id)
        
        if not contribution:
            return jsonify({'error': 'Contribution not found'}), 404
        
        contrib_dict = contribution.to_dict()
        
        if contribution.pool:
            contrib_dict['pool'] = contribution.pool.to_dict()
        
        return jsonify({
            'success': True,
            'contribution': contrib_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get contribution: {str(e)}")
        return jsonify({'error': 'Failed to get contribution'}), 500


@contributions_bp.route('/estimate', methods=['POST'])
def estimate_contribution_value():
    """Estimate the value of a potential contribution."""
    try:
        data = request.get_json()
        
        pool_id = data.get('pool_id')
        quantity_tons = data.get('quantity_tons')
        
        if not pool_id or not quantity_tons:
            return jsonify({'error': 'pool_id and quantity_tons are required'}), 400
        
        estimation = FinancialService.estimate_contribution_value(pool_id, quantity_tons)
        
        if 'error' in estimation:
            return jsonify({'error': estimation['error']}), 400
        
        return jsonify({
            'success': True,
            **estimation
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to estimate contribution value: {str(e)}")
        return jsonify({'error': 'Failed to estimate value'}), 500


@contributions_bp.route('/user/<int:user_id>/earnings', methods=['GET'])
def get_user_earnings(user_id):
    """Get earnings summary for a user across all pools."""
    try:
        summary = FinancialService.get_user_earnings_summary(user_id)
        
        if 'error' in summary:
            return jsonify({'error': summary['error']}), 400
        
        return jsonify({
            'success': True,
            **summary
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get user earnings: {str(e)}")
        return jsonify({'error': 'Failed to get earnings'}), 500


@contributions_bp.route('/<int:contribution_id>/payout', methods=['POST'])
def trigger_payout(contribution_id):
    """Trigger bank transfer simulation for a contribution."""
    try:
        result = FinancialService.simulate_bank_transfer(contribution_id)
        
        if not result['success']:
            return jsonify({'error': result['message']}), 400
        
        return jsonify({
            'success': True,
            **result
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to trigger payout: {str(e)}")
        return jsonify({'error': 'Failed to trigger payout'}), 500


@contributions_bp.route('/stats', methods=['GET'])
def get_contribution_stats():
    """Get global contribution statistics."""
    try:
        from backend.extensions import db
        from sqlalchemy import func
        
        total_contributions = PoolContribution.query.count()
        total_quantity = db.session.query(func.sum(PoolContribution.quantity_tons)).scalar() or 0
        total_paid = db.session.query(func.sum(PoolContribution.actual_payout)).filter(
            PoolContribution.payout_status == 'PAID'
        ).scalar() or 0
        
        unique_contributors = db.session.query(func.count(func.distinct(PoolContribution.user_id))).scalar()
        
        return jsonify({
            'success': True,
            'total_contributions': total_contributions,
            'total_quantity_tons': float(total_quantity),
            'total_paid_amount': float(total_paid),
            'unique_contributors': unique_contributors
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get contribution stats: {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500
