"""
Yield Pool API Endpoints
"""

from flask import Blueprint, request, jsonify
from backend.models import YieldPool, PoolContribution,  ResourceShare
from backend.services.pool_service import PoolService
from backend.services.financial_service import FinancialService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

pools_bp = Blueprint('pools', __name__, url_prefix='/api/v1/pools')


@pools_bp.route('', methods=['POST'])
def create_pool():
    """Create a new yield pool."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['pool_name', 'crop_type', 'target_quantity', 'min_price_per_ton', 'collection_location']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        creator_id = data.get('creator_id', 1)  # TODO: Get from JWT
        
        pool, error = PoolService.create_pool(data, creator_id)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'pool': pool.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create pool: {str(e)}")
        return jsonify({'error': 'Failed to create pool'}), 500


@pools_bp.route('', methods=['GET'])
def list_pools():
    """List all yield pools with optional filters."""
    try:
        status = request.args.get('status')
        crop_type = request.args.get('crop_type')
        
        query = YieldPool.query
        
        if status:
            query = query.filter_by(status=status)
        if crop_type:
            query = query.filter(YieldPool.crop_type.ilike(f'%{crop_type}%'))
        
        pools = query.order_by(YieldPool.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'count': len(pools),
            'pools': [p.to_dict() for p in pools]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to list pools: {str(e)}")
        return jsonify({'error': 'Failed to list pools'}), 500


@pools_bp.route('/<int:pool_id>', methods=['GET'])
def get_pool(pool_id):
    """Get detailed information about a specific pool."""
    try:
        stats = PoolService.get_pool_statistics(pool_id)
        
        if not stats:
            return jsonify({'error': 'Pool not found'}), 404
        
        return jsonify({
            'success': True,
            **stats
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get pool: {str(e)}")
        return jsonify({'error': 'Failed to get pool'}), 500


@pools_bp.route('/<int:pool_id>/state', methods=['POST'])
def transition_pool_state(pool_id):
    """Transition pool to a new state."""
    try:
        data = request.get_json()
        new_state = data.get('state')
        user_id = data.get('user_id', 1)  # TODO: Get from JWT
        
        if not new_state:
            return jsonify({'error': 'State is required'}), 400
        
        success, error = PoolService.transition_state(pool_id, new_state, user_id)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'message': f'Pool transitioned to {new_state}'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to transition pool state: {str(e)}")
        return jsonify({'error': 'Failed to transition state'}), 500


@pools_bp.route('/<int:pool_id>/offer', methods=['POST'])
def set_buyer_offer(pool_id):
    """Set a buyer's offer for the pool."""
    try:
        data = request.get_json()
        
        buyer_name = data.get('buyer_name')
        offer_price = data.get('offer_price')
        
        if not buyer_name or not offer_price:
            return jsonify({'error': 'buyer_name and offer_price are required'}), 400
        
        success, error = PoolService.set_buyer_offer(pool_id, buyer_name, offer_price)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'message': 'Offer set successfully',
            'offer_price': offer_price,
            'buyer_name': buyer_name
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to set buyer offer: {str(e)}")
        return jsonify({'error': 'Failed to set offer'}), 500


@pools_bp.route('/<int:pool_id>/vote', methods=['POST'])
def record_vote(pool_id):
    """Record a pool member's vote on a buyer offer."""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id', 1)  # TODO: Get from JWT
        vote = data.get('vote')
        comment = data.get('comment')
        
        if vote not in ['ACCEPT', 'REJECT']:
            return jsonify({'error': 'Vote must be ACCEPT or REJECT'}), 400
        
        pool_vote, error = PoolService.record_vote(pool_id, user_id, vote, comment)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Get updated voting status
        voting_status = PoolService.get_voting_status(pool_id)
        
        return jsonify({
            'success': True,
            'vote': pool_vote.to_dict(),
            'voting_status': voting_status
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to record vote: {str(e)}")
        return jsonify({'error': 'Failed to record vote'}), 500


@pools_bp.route('/<int:pool_id>/voting-status', methods=['GET'])
def get_voting_status(pool_id):
    """Get current voting status for a pool."""
    try:
        status = PoolService.get_voting_status(pool_id)
        
        if not status:
            return jsonify({'error': 'No active voting or pool not found'}), 404
        
        return jsonify({
            'success': True,
            **status
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get voting status: {str(e)}")
        return jsonify({'error': 'Failed to get voting status'}), 500


@pools_bp.route('/<int:pool_id>/distribution', methods=['GET'])
def get_distribution(pool_id):
    """Get profit distribution calculation for a pool."""
    try:
        distribution = FinancialService.calculate_distribution(pool_id)
        
        if 'error' in distribution:
            return jsonify({'error': distribution['error']}), 400
        
        return jsonify({
            'success': True,
            **distribution
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get distribution: {str(e)}")
        return jsonify({'error': 'Failed to get distribution'}), 500


@pools_bp.route('/<int:pool_id>/distribute', methods=['POST'])
def execute_distribution(pool_id):
    """Execute profit distribution to all pool members."""
    try:
        success, message = FinancialService.execute_distribution(pool_id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to execute distribution: {str(e)}")
        return jsonify({'error': 'Failed to execute distribution'}), 500


@pools_bp.route('/<int:pool_id>/resources', methods=['GET'])
def get_shared_resources(pool_id):
    """Get all shared resources for a pool."""
    try:
        resources = ResourceShare.query.filter_by(pool_id=pool_id).all()
        
        return jsonify({
            'success': True,
            'count': len(resources),
            'resources': [r.to_dict() for r in resources]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get resources: {str(e)}")
        return jsonify({'error': 'Failed to get resources'}), 500


@pools_bp.route('/<int:pool_id>/resources', methods=['POST'])
def share_resource(pool_id):
    """Share a resource with the pool."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)  # TODO: Get from JWT
        
        required = ['resource_type', 'resource_name']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        resource, error = PoolService.share_resource(pool_id, user_id, data)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'resource': resource.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to share resource: {str(e)}")
        return jsonify({'error': 'Failed to share resource'}), 500


@pools_bp.route('/roi-comparison', methods=['POST'])
def compare_roi():
    """Compare pool participation vs solo selling."""
    try:
        data = request.get_json()
        
        pool_id = data.get('pool_id')
        solo_price = data.get('solo_price_per_ton')
        
        if not pool_id or not solo_price:
            return jsonify({'error': 'pool_id and solo_price_per_ton are required'}), 400
        
        comparison = FinancialService.calculate_roi_comparison(pool_id, solo_price)
        
        if 'error' in comparison:
            return jsonify({'error': comparison['error']}), 400
        
        return jsonify({
            'success': True,
            **comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to compare ROI: {str(e)}")
        return jsonify({'error': 'Failed to compare ROI'}), 500
