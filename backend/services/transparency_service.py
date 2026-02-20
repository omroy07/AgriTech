from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.traceability import SupplyBatch
from backend.models.processing import ProcessingBatch
from backend.models.warehouse import StockItem
from backend.models.soil_health import SoilTest
from backend.models.transparency import ProduceReview, PriceAdjustmentLog
from backend.models.forum import UserReputation
from backend.models.user import User
import math

class TransparencyService:
    @staticmethod
    def get_seed_to_shelf_genealogy(stock_item_id):
        """
        Recursively traces a StockItem back to its origin SupplyBatch and SoilTest.
        """
        item = StockItem.query.get(stock_item_id)
        if not item:
            return None

        genealogy = {
            "retail_item": item.to_dict(),
            "journey": []
        }

        # Step 1: Trace to Processing Batch
        if item.processing_batch_id:
            p_batch = ProcessingBatch.query.get(item.processing_batch_id)
            if p_batch:
                genealogy["processing"] = p_batch.to_dict()
                # Trace Processing to Supply Batches
                supply_batches = p_batch.supply_batches
                genealogy["origins"] = []
                for s_batch in supply_batches:
                    genealogy["origins"].append(TransparencyService._trace_supply_batch(s_batch))
        
        # Step 2: direct trace to Supply Batch (if no processing)
        elif item.supply_batch_id:
            s_batch = SupplyBatch.query.get(item.supply_batch_id)
            if s_batch:
                genealogy["origins"] = [TransparencyService._trace_supply_batch(s_batch)]

        return genealogy

    @staticmethod
    def _trace_supply_batch(batch):
        """Internal helper to trace a supply batch back to farmer and soil."""
        data = batch.to_dict(include_logs=True)
        
        # Farmer info
        farmer = User.query.get(batch.farmer_id)
        if farmer:
            data["farmer_name"] = farmer.username
            reputation = UserReputation.query.filter_by(user_id=farmer.id).first()
            data["farmer_reputation"] = reputation.reputation_score if reputation else 0

        # Soil info
        if batch.soil_test_id:
            soil = SoilTest.query.get(batch.soil_test_id)
            if soil:
                data["soil_profile"] = soil.to_dict()
        
        return data

    @staticmethod
    def calculate_nutritional_decay(stock_item):
        """
        Hard Requirement: Nutritional Decay Algorithm.
        Adjusts price based on harvest age and storage temp/humidity.
        """
        # 1. Harvest Age Factor
        harvest_date = None
        if stock_item.supply_batch_id:
            s_batch = SupplyBatch.query.get(stock_item.supply_batch_id)
            harvest_date = s_batch.harvest_date
        elif stock_item.processing_batch_id:
            p_batch = ProcessingBatch.query.get(stock_item.processing_batch_id)
            # Find earliest harvest among origins
            if p_batch.supply_batches:
                harvest_date = min([b.harvest_date for b in p_batch.supply_batches])
        
        if not harvest_date:
            return stock_item.base_price, 100.0

        age_days = (datetime.utcnow() - harvest_date).days
        age_hours = (datetime.utcnow() - harvest_date).total_seconds() / 3600

        # 2. Decay Model (Simplified Exponential)
        # Assuming half-life of 7 days for peak freshness
        decay_constant = 0.0041 # ln(2) / (7 * 24)
        freshness = 100 * math.exp(-decay_constant * age_hours)
        
        # 3. Storage Penalty (Mocked from Warehouse logs)
        # In a real system, we'd query TelemetryLog for abnormal temps
        penalty = 1.0 # No penalty
        
        final_score = max(0, min(100, freshness * penalty))
        
        # 4. Dynamic Pricing
        # Price drops faster as freshness approaches zero
        # If freshness is 50%, price might be 70%. If freshness 20%, price might be 30%.
        price_ratio = (final_score / 100.0) ** 0.5 # Square root for slower price drop initially
        new_price = stock_item.base_price * price_ratio
        
        return round(new_price, 2), round(final_score, 1)

    @staticmethod
    def process_consumer_feedback(user_id, stock_item_id, rating, comment):
        """
        Hard Requirement: Reputation Feedback Loop.
        Reverse-maps review to original farmer and updates reputation.
        """
        item = StockItem.query.get(stock_item_id)
        if not item:
            return None
            
        # Create review
        review = ProduceReview(
            user_id=user_id,
            stock_item_id=stock_item_id,
            rating=rating,
            comment=comment,
            processing_batch_id=item.processing_batch_id,
            supply_batch_id=item.supply_batch_id
        )
        
        # Trace to Farmer(s)
        producers = []
        if item.processing_batch_id:
            pb = ProcessingBatch.query.get(item.processing_batch_id)
            for sb in pb.supply_batches:
                producers.append(sb.farmer_id)
        elif item.supply_batch_id:
            producers.append(SupplyBatch.query.get(item.supply_batch_id).farmer_id)
            
        producers = list(set(producers)) # Unique farmers
        
        db.session.add(review)
        
        # Update Farmer Reputation
        # Logic: 5 star = +5 points, 1 star = -10 points
        point_map = {1: -10, 2: -5, 3: 0, 4: 2, 5: 5}
        points = point_map.get(rating, 0)
        
        for farmer_id in producers:
            rep = UserReputation.query.filter_by(user_id=farmer_id).first()
            if not rep:
                rep = UserReputation(user_id=farmer_id, reputation_score=100)
                db.session.add(rep)
            
            rep.reputation_score += points
            rep.reputation_score = max(0, rep.reputation_score)
            
        db.session.commit()
        return review

    @staticmethod
    def run_hourly_pricing_adjustment():
        """
        Hourly Celery task target.
        """
        items = StockItem.query.filter(StockItem.current_quantity > 0).all()
        adjustments = 0
        
        for item in items:
            old_price = item.current_market_price or item.base_price
            new_price, score = TransparencyService.calculate_nutritional_decay(item)
            
            if abs(new_price - old_price) > 0.01:
                log = PriceAdjustmentLog(
                    stock_item_id=item.id,
                    old_price=old_price,
                    new_price=new_price,
                    freshness_score=score,
                    adjustment_reason="HOURLY_DECAY"
                )
                item.current_market_price = new_price
                item.freshness_score = score
                db.session.add(log)
                adjustments += 1
                
        db.session.commit()
        return adjustments
