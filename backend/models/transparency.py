from datetime import datetime
from backend.extensions import db

class ProduceReview(db.Model):
    __tablename__ = 'produce_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False) # 1-5
    comment = db.Column(db.Text)
    
    # Traceability Context (captured at time of review)
    processing_batch_id = db.Column(db.Integer, db.ForeignKey('processing_batches.id'))
    supply_batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id'))
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    is_processed_for_reputation = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

class PriceAdjustmentLog(db.Model):
    """Logs hourly price changes based on nutritional decay/freshness."""
    __tablename__ = 'price_adjustment_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    
    old_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    freshness_score = db.Column(db.Float)
    
    adjustment_reason = db.Column(db.String(100)) # e.g., "HOURLY_DECAY", "STORAGE_ANOMALY"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'old_price': self.old_price,
            'new_price': self.new_price,
            'reason': self.adjustment_reason,
            'timestamp': self.timestamp.isoformat()
        }
