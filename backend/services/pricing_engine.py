import json
import logging

logger = logging.getLogger(__name__)

class PricingEngine:
    """
    Logic for volume-based pricing, tax calculation, and shipping estimations.
    """
    
    @staticmethod
    def calculate_unit_price(item, quantity):
        """Determine price based on volume tiers"""
        try:
            tiers = json.loads(item.volume_pricing) if item.volume_pricing else []
            # Sort tiers by min quantity descending
            sorted_tiers = sorted(tiers, key=lambda x: x['min'], reverse=True)
            
            for tier in sorted_tiers:
                if quantity >= tier['min']:
                    return float(tier['price'])
                    
            return float(item.base_price)
        except Exception as e:
            logger.error(f"Pricing calculation failed: {str(e)}")
            return float(item.base_price)

    @staticmethod
    def calculate_tax(subtotal, tax_rate=0.05):
        """Standard agricultural tax logic (e.g., 5% GST/VAT)"""
        return round(subtotal * tax_rate, 2)

    @staticmethod
    def estimate_shipping(origin_loc, dest_loc, weight):
        """Mock logic for estimating bulk logistics costs"""
        # Base cost + weight factor
        return round(150.0 + (weight * 0.5), 2)
