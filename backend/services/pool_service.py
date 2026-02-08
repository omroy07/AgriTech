"""
Yield Pool Service: State machine and business logic for collaborative farming pools.
"""

from backend.models import YieldPool, PoolContribution, ResourceShare, PoolVote, User
from backend.extensions import db
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class PoolService:
    """Service for managing yield pool lifecycle and operations."""
    
    # Pool state constants
    STATE_OPEN = 'OPEN'
    STATE_LOCKED = 'LOCKED'
    STATE_COMPLETED = 'COMPLETED'
    STATE_DISTRIBUTED = 'DISTRIBUTED'
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        STATE_OPEN: [STATE_LOCKED],
        STATE_LOCKED: [STATE_COMPLETED, STATE_OPEN],  # Can reopen if deal falls through
        STATE_COMPLETED: [STATE_DISTRIBUTED],
        STATE_DISTRIBUTED: []  # Terminal state
    }
    
    @staticmethod
    def create_pool(pool_data, creator_id):
        """
        Create a new yield pool.
        
        Args:
            pool_data (dict): Pool configuration
            creator_id (int): User ID of pool creator
            
        Returns:
            tuple: (YieldPool, error_message)
        """
        try:
            # Generate unique pool ID
            pool_id = f"POOL-{uuid.uuid4().hex[:12].upper()}"
            
            # Create pool
            pool = YieldPool(
                pool_id=pool_id,
                pool_name=pool_data['pool_name'],
                crop_type=pool_data['crop_type'],
                target_quantity=pool_data['target_quantity'],
                min_price_per_ton=pool_data['min_price_per_ton'],
                collection_location=pool_data['collection_location'],
                logistics_overhead_percent=pool_data.get('logistics_overhead_percent', 5.0),
                status=PoolService.STATE_OPEN
            )
            
            db.session.add(pool)
            db.session.commit()
            
            logger.info(f"Pool created: {pool_id} by user {creator_id}")
            return pool, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create pool: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def add_contribution(pool_id, user_id, quantity_tons, quality_grade='A'):
        """
        Add a farmer's contribution to the pool.
        
        Args:
            pool_id (int): Pool database ID
            user_id (int): Contributing farmer's user ID
            quantity_tons (float): Quantity contributed in tons
            quality_grade (str): Quality grade (A, B, C)
            
        Returns:
            tuple: (PoolContribution, error_message)
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return None, "Pool not found"
            
            if pool.status != PoolService.STATE_OPEN:
                return None, f"Pool is {pool.status}, contributions not allowed"
            
            # Check if user already contributed
            existing = PoolContribution.query.filter_by(
                pool_id=pool_id,
                user_id=user_id
            ).first()
            
            if existing:
                # Update existing contribution
                existing.quantity_tons += quantity_tons
                existing.contributed_at = datetime.utcnow()
                contribution = existing
                logger.info(f"Updated contribution for user {user_id} in pool {pool.pool_id}")
            else:
                # Create new contribution
                contribution = PoolContribution(
                    pool_id=pool_id,
                    user_id=user_id,
                    quantity_tons=quantity_tons,
                    quality_grade=quality_grade
                )
                db.session.add(contribution)
                logger.info(f"New contribution from user {user_id} in pool {pool.pool_id}")
            
            # Update pool current quantity
            pool.current_quantity = db.session.query(
                db.func.sum(PoolContribution.quantity_tons)
            ).filter_by(pool_id=pool_id).scalar() or 0.0
            
            # Recalculate contribution percentages
            PoolService._recalculate_percentages(pool)
            
            db.session.commit()
            
            return contribution, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to add contribution: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def _recalculate_percentages(pool):
        """Recalculate contribution percentages for all pool members."""
        if pool.current_quantity == 0:
            return
        
        for contribution in pool.contributions:
            contribution.contribution_percentage = (
                contribution.quantity_tons / pool.current_quantity * 100
            )
    
    @staticmethod
    def transition_state(pool_id, new_state, user_id=None):
        """
        Transition pool to a new state.
        
        Args:
            pool_id (int): Pool database ID
            new_state (str): Target state
            user_id (int): User requesting transition
            
        Returns:
            tuple: (bool success, error_message)
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return False, "Pool not found"
            
            # Validate transition
            current_state = pool.status
            if new_state not in PoolService.VALID_TRANSITIONS.get(current_state, []):
                return False, f"Invalid transition from {current_state} to {new_state}"
            
            # State-specific validations and actions
            if new_state == PoolService.STATE_LOCKED:
                if pool.current_quantity < pool.target_quantity * 0.8:
                    return False, "Pool must be at least 80% filled to lock"
                pool.locked_at = datetime.utcnow()
            
            elif new_state == PoolService.STATE_COMPLETED:
                if not pool.current_offer_price:
                    return False, "No accepted offer price set"
                pool.completed_at = datetime.utcnow()
            
            elif new_state == PoolService.STATE_DISTRIBUTED:
                # Check all payouts are completed
                pending = PoolContribution.query.filter_by(
                    pool_id=pool_id,
                    payout_status='PENDING'
                ).count()
                
                if pending > 0:
                    return False, f"{pending} payouts still pending"
                
                pool.distributed_at = datetime.utcnow()
            
            # Update state
            pool.status = new_state
            db.session.commit()
            
            logger.info(f"Pool {pool.pool_id} transitioned from {current_state} to {new_state}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to transition pool state: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def set_buyer_offer(pool_id, buyer_name, offer_price):
        """
        Set a buyer's offer price for the pool.
        
        Args:
            pool_id (int): Pool database ID
            buyer_name (str): Name of buyer/factory
            offer_price (float): Offered price per ton
            
        Returns:
            tuple: (bool success, error_message)
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return False, "Pool not found"
            
            if pool.status not in [PoolService.STATE_LOCKED, PoolService.STATE_OPEN]:
                return False, f"Cannot set offer when pool is {pool.status}"
            
            if offer_price < pool.min_price_per_ton:
                logger.warning(f"Offer price {offer_price} below minimum {pool.min_price_per_ton}")
            
            pool.buyer_name = buyer_name
            pool.current_offer_price = offer_price
            
            db.session.commit()
            
            logger.info(f"Buyer offer set for pool {pool.pool_id}: {buyer_name} at {offer_price}/ton")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to set buyer offer: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def record_vote(pool_id, user_id, vote, comment=None):
        """
        Record a pool member's vote on a buyer offer.
        
        Args:
            pool_id (int): Pool database ID
            user_id (int): Voting user ID
            vote (str): 'ACCEPT' or 'REJECT'
            comment (str): Optional comment
            
        Returns:
            tuple: (PoolVote, error_message)
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return None, "Pool not found"
            
            if not pool.current_offer_price:
                return None, "No active offer to vote on"
            
            # Check if user is a contributor
            contribution = PoolContribution.query.filter_by(
                pool_id=pool_id,
                user_id=user_id
            ).first()
            
            if not contribution:
                return None, "Only contributors can vote"
            
            # Check if already voted
            existing_vote = PoolVote.query.filter_by(
                pool_id=pool_id,
                user_id=user_id,
                offer_price=pool.current_offer_price
            ).first()
            
            if existing_vote:
                # Update vote
                existing_vote.vote = vote
                existing_vote.comment = comment
                existing_vote.voted_at = datetime.utcnow()
                pool_vote = existing_vote
            else:
                # Create new vote
                pool_vote = PoolVote(
                    pool_id=pool_id,
                    user_id=user_id,
                    vote=vote,
                    offer_price=pool.current_offer_price,
                    comment=comment
                )
                db.session.add(pool_vote)
            
            db.session.commit()
            
            # Check if voting is complete
            PoolService._check_voting_complete(pool)
            
            logger.info(f"Vote recorded: user {user_id} voted {vote} on pool {pool.pool_id}")
            return pool_vote, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record vote: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def _check_voting_complete(pool):
        """Check if voting is complete and take action if consensus reached."""
        total_contributors = len(pool.contributions)
        
        if total_contributors == 0:
            return
        
        # Get votes for current offer
        votes = PoolVote.query.filter_by(
            pool_id=pool.id,
            offer_price=pool.current_offer_price
        ).all()
        
        if len(votes) < total_contributors:
            logger.info(f"Voting incomplete: {len(votes)}/{total_contributors} votes")
            return
        
        # Count accept/reject
        accept_votes = sum(1 for v in votes if v.vote == 'ACCEPT')
        reject_votes = sum(1 for v in votes if v.vote == 'REJECT')
        
        # Require >50% acceptance
        if accept_votes > total_contributors / 2:
            logger.info(f"Pool {pool.pool_id} offer ACCEPTED by consensus")
            # Transition to completed (will be done by admin/task)
        else:
            logger.info(f"Pool {pool.pool_id} offer REJECTED by consensus")
            # Reset offer
            pool.current_offer_price = None
            pool.buyer_name = None
            db.session.commit()
    
    @staticmethod
    def get_voting_status(pool_id):
        """
        Get current voting status for a pool.
        
        Returns:
            dict: Voting statistics
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool or not pool.current_offer_price:
                return None
            
            total_contributors = len(pool.contributions)
            votes = PoolVote.query.filter_by(
                pool_id=pool_id,
                offer_price=pool.current_offer_price
            ).all()
            
            accept_count = sum(1 for v in votes if v.vote == 'ACCEPT')
            reject_count = sum(1 for v in votes if v.vote == 'REJECT')
            
            return {
                'total_contributors': total_contributors,
                'votes_received': len(votes),
                'accept_count': accept_count,
                'reject_count': reject_count,
                'voting_complete': len(votes) >= total_contributors,
                'consensus_reached': accept_count > total_contributors / 2,
                'offer_price': pool.current_offer_price,
                'buyer_name': pool.buyer_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get voting status: {str(e)}")
            return None
    
    @staticmethod
    def share_resource(pool_id, owner_id, resource_data):
        """
        Share a physical resource with the pool.
        
        Args:
            pool_id (int): Pool database ID
            owner_id (int): Resource owner user ID
            resource_data (dict): Resource details
            
        Returns:
            tuple: (ResourceShare, error_message)
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return None, "Pool not found"
            
            # Check if user is a contributor
            contribution = PoolContribution.query.filter_by(
                pool_id=pool_id,
                user_id=owner_id
            ).first()
            
            if not contribution:
                return None, "Only pool contributors can share resources"
            
            # Create resource share
            resource = ResourceShare(
                pool_id=pool_id,
                owner_id=owner_id,
                resource_type=resource_data['resource_type'],
                resource_name=resource_data['resource_name'],
                resource_value=resource_data.get('resource_value', 0.0),
                usage_cost_per_hour=resource_data.get('usage_cost_per_hour', 0.0),
                is_free_for_pool=resource_data.get('is_free_for_pool', True)
            )
            
            db.session.add(resource)
            db.session.commit()
            
            logger.info(f"Resource shared: {resource.resource_name} by user {owner_id} in pool {pool.pool_id}")
            return resource, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to share resource: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_pool_statistics(pool_id):
        """Get comprehensive statistics for a pool."""
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return None
            
            stats = {
                'pool': pool.to_dict(),
                'total_contributors': len(pool.contributions),
                'total_quantity': pool.current_quantity,
                'fill_percentage': (pool.current_quantity / pool.target_quantity * 100) if pool.target_quantity > 0 else 0,
                'shared_resources': len(pool.shared_resources),
                'status': pool.status
            }
            
            if pool.current_offer_price:
                stats['voting'] = PoolService.get_voting_status(pool_id)
                stats['estimated_total_value'] = pool.current_quantity * pool.current_offer_price
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get pool statistics: {str(e)}")
            return None
