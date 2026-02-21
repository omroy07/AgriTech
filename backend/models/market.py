from datetime import datetime
from backend.extensions import db

class ForwardContract(db.Model):
    __tablename__ = 'forward_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id')) # Optional until harvest
    
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Could be a vendor or broker
    
    crop_type = db.Column(db.String(100), nullable=False)
    estimated_quantity = db.Column(db.Float, nullable=False)
    locked_price_per_unit = db.Column(db.Float, nullable=False)
    
    contract_date = db.Column(db.DateTime, default=datetime.utcnow)
    maturity_date = db.Column(db.DateTime, nullable=False) # Estimated harvest date
    
    # Status: DRAFT, OPEN, SIGNED, EXECUTED, CANCELLED
    status = db.Column(db.String(20), default='DRAFT')
    
    # Hedging Metadata (L3-1560)
    hedge_ratio = db.Column(db.Float) # Percentage of total yield locked in
    market_volatility_at_lock = db.Column(db.Float)
    
    # Cascading Quality Adjustments (L3-1604)
    quality_penalty_clause = db.Column(db.Float, default=0.0) # Percentage deduction from final payout
    
    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'crop': self.crop_type,
            'quantity': self.estimated_quantity,
            'price': self.locked_price_per_unit,
            'maturity': self.maturity_date.isoformat(),
            'status': self.status,
            'hedge_ratio': self.hedge_ratio
        }

class PriceHedgingLog(db.Model):
    __tablename__ = 'price_hedging_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    action = db.Column(db.String(50)) # e.g., "AUTO_HEDGE_ADJUSTMENT"
    old_hedge_ratio = db.Column(db.Float)
    new_hedge_ratio = db.Column(db.Float)
    
    trigger_reason = db.Column(db.String(255)) # e.g., "High Weather Volatility"
    market_price_snapshot = db.Column(db.Float)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
