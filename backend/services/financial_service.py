"""
Financial Service: Handles profit distribution and financial calculations for yield pools.
"""

from backend.models import YieldPool, PoolContribution
from backend.extensions import db
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)


class FinancialService:
    """Service for managing pool financial operations and profit distribution."""
    
    @staticmethod
    def calculate_distribution(pool_id):
        """
        Calculate profit distribution for all pool contributors.
        
        Args:
            pool_id (int): Pool database ID
            
        Returns:
            dict: Distribution breakdown
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return None
            
            if not pool.current_offer_price:
                return {'error': 'No accepted offer price'}
            
            # Calculate total revenue
            total_revenue = Decimal(str(pool.current_quantity)) * Decimal(str(pool.current_offer_price))
            
            # Calculate logistics overhead
            logistics_cost = total_revenue * (Decimal(str(pool.logistics_overhead_percent)) / Decimal('100'))
            
            # Net distributable amount
            net_amount = total_revenue - logistics_cost
            
            # Calculate individual payouts
            distributions = []
            total_distributed = Decimal('0')
            
            for contribution in pool.contributions:
                # Calculate payout based on contribution percentage
                contribution_decimal = Decimal(str(contribution.contribution_percentage)) / Decimal('100')
                payout = (net_amount * contribution_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
                distributions.append({
                    'user_id': contribution.user_id,
                    'username': contribution.user.username if contribution.user else None,
                    'quantity_tons': float(contribution.quantity_tons),
                    'contribution_percentage': float(contribution.contribution_percentage),
                    'payout': float(payout),
                    'quality_grade': contribution.quality_grade
                })
                
                total_distributed += payout
            
            # Handle rounding differences (distribute to largest contributor)
            rounding_difference = net_amount - total_distributed
            if rounding_difference != 0 and distributions:
                largest = max(distributions, key=lambda x: x['payout'])
                largest['payout'] += float(rounding_difference)
            
            return {
                'pool_id': pool.pool_id,
                'status': pool.status,
                'total_quantity_tons': float(pool.current_quantity),
                'price_per_ton': float(pool.current_offer_price),
                'gross_revenue': float(total_revenue),
                'logistics_overhead_percent': float(pool.logistics_overhead_percent),
                'logistics_cost': float(logistics_cost),
                'net_distributable': float(net_amount),
                'total_distributed': float(total_distributed),
                'distributions': distributions,
                'buyer_name': pool.buyer_name
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate distribution: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def execute_distribution(pool_id):
        """
        Execute the profit distribution and update payout status.
        
        This simulates bank transfers/payments to contributors.
        
        Args:
            pool_id (int): Pool database ID
            
        Returns:
            tuple: (bool success, message)
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return False, "Pool not found"
            
            if pool.status != 'COMPLETED':
                return False, f"Pool must be in COMPLETED state, currently {pool.status}"
            
            # Calculate distribution
            distribution = FinancialService.calculate_distribution(pool_id)
            
            if 'error' in distribution:
                return False, distribution['error']
            
            # Update each contribution with actual payout
            for dist in distribution['distributions']:
                contribution = PoolContribution.query.filter_by(
                    pool_id=pool_id,
                    user_id=dist['user_id']
                ).first()
                
                if contribution:
                    contribution.actual_payout = dist['payout']
                    contribution.payout_status = 'PAID'
                    contribution.paid_at = datetime.utcnow()
                    
                    logger.info(f"Payout executed: User {dist['user_id']} received {dist['payout']}")
            
            db.session.commit()
            
            logger.info(f"Distribution executed for pool {pool.pool_id}, total: {distribution['total_distributed']}")
            return True, f"Successfully distributed {distribution['total_distributed']}"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to execute distribution: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def simulate_bank_transfer(contribution_id):
        """
        Simulate a bank transfer for a specific contribution.
        
        In production, this would integrate with payment gateways.
        
        Args:
            contribution_id (int): PoolContribution ID
            
        Returns:
            dict: Transfer result
        """
        try:
            contribution = PoolContribution.query.get(contribution_id)
            
            if not contribution:
                return {'success': False, 'message': 'Contribution not found'}
            
            if contribution.payout_status == 'PAID':
                return {'success': False, 'message': 'Already paid'}
            
            if not contribution.actual_payout:
                return {'success': False, 'message': 'Payout amount not calculated'}
            
            # Simulate transfer (in production: API call to payment gateway)
            # For now, just update status
            contribution.payout_status = 'PAID'
            contribution.paid_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Simulated bank transfer: {contribution.actual_payout} to user {contribution.user_id}")
            
            return {
                'success': True,
                'message': 'Transfer completed',
                'amount': contribution.actual_payout,
                'user_id': contribution.user_id,
                'transaction_id': f"TXN-{contribution.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to simulate bank transfer: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_earnings_summary(user_id):
        """
        Get a summary of a user's earnings across all pools.
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Earnings summary
        """
        try:
            contributions = PoolContribution.query.filter_by(user_id=user_id).all()
            
            total_contributed_tons = sum(c.quantity_tons for c in contributions)
            total_earned = sum(c.actual_payout or 0 for c in contributions)
            pending_payout = sum(
                c.estimated_value for c in contributions
                if c.payout_status == 'PENDING'
            )
            
            pools_participated = len(set(c.pool_id for c in contributions))
            
            return {
                'user_id': user_id,
                'total_contributed_tons': total_contributed_tons,
                'total_earned': total_earned,
                'pending_payout': pending_payout,
                'pools_participated': pools_participated,
                'contributions': [c.to_dict() for c in contributions]
            }
            
        except Exception as e:
            logger.error(f"Failed to get earnings summary: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def estimate_contribution_value(pool_id, quantity_tons):
        """
        Estimate the value of a potential contribution.
        
        Args:
            pool_id (int): Pool database ID
            quantity_tons (float): Proposed contribution quantity
            
        Returns:
            dict: Value estimation
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool:
                return {'error': 'Pool not found'}
            
            # Use current offer or minimum price
            price_per_ton = pool.current_offer_price or pool.min_price_per_ton
            
            # Calculate gross value
            gross_value = quantity_tons * price_per_ton
            
            # Estimate net after logistics
            logistics_deduction = gross_value * (pool.logistics_overhead_percent / 100)
            estimated_net = gross_value - logistics_deduction
            
            # Calculate would-be percentage
            would_be_total = pool.current_quantity + quantity_tons
            would_be_percentage = (quantity_tons / would_be_total * 100) if would_be_total > 0 else 0
            
            return {
                'quantity_tons': quantity_tons,
                'price_per_ton': price_per_ton,
                'gross_value': gross_value,
                'logistics_deduction': logistics_deduction,
                'estimated_net_payout': estimated_net,
                'would_be_percentage': would_be_percentage,
                'pool_current_quantity': pool.current_quantity,
                'pool_target_quantity': pool.target_quantity
            }
            
        except Exception as e:
            logger.error(f"Failed to estimate contribution value: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def calculate_roi_comparison(pool_id, solo_price_per_ton):
        """
        Compare pool participation ROI vs selling solo.
        
        Args:
            pool_id (int): Pool database ID
            solo_price_per_ton (float): Price farmer would get selling alone
            
        Returns:
            dict: ROI comparison
        """
        try:
            pool = YieldPool.query.get(pool_id)
            
            if not pool or not pool.current_offer_price:
                return {'error': 'Pool or offer not available'}
            
            # Pool price after logistics
            pool_net_price = pool.current_offer_price * (1 - pool.logistics_overhead_percent / 100)
            
            # Calculate advantage
            price_difference = pool_net_price - solo_price_per_ton
            percentage_gain = (price_difference / solo_price_per_ton * 100) if solo_price_per_ton > 0 else 0
            
            return {
                'solo_price_per_ton': solo_price_per_ton,
                'pool_gross_price_per_ton': pool.current_offer_price,
                'pool_logistics_overhead': pool.logistics_overhead_percent,
                'pool_net_price_per_ton': pool_net_price,
                'price_difference': price_difference,
                'percentage_gain': percentage_gain,
                'recommendation': 'JOIN_POOL' if percentage_gain > 0 else 'SELL_SOLO',
                'buyer_name': pool.buyer_name
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate ROI comparison: {str(e)}")
            return {'error': str(e)}
