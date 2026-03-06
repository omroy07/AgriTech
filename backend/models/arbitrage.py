from datetime import datetime
from backend.extensions import db

class ArbitrageOpportunity(db.Model):
    """
    Algorithmic Commodity Arbitrage Trade Opportunity.
    Maps out price inefficiencies across geographic regions driven by spatial yield prophecies.
    """
    __tablename__ = 'arbitrage_opportunities'

    id = db.Column(db.Integer, primary_key=True)
    commodity_type = db.Column(db.String(100), nullable=False)
    
    # Buy Leg (Oversupplied Region)
    source_grid_id = db.Column(db.Integer, db.ForeignKey('spatial_yield_grids.id'), nullable=False)
    source_price_per_kg = db.Column(db.Float, nullable=False)
    
    # Sell Leg (Undersupplied Region)
    target_grid_id = db.Column(db.Integer, db.ForeignKey('spatial_yield_grids.id'), nullable=False)
    target_price_per_kg = db.Column(db.Float, nullable=False)
    
    # Logistics Costs Modelled
    estimated_transport_cost_usd = db.Column(db.Float, nullable=False)
    carbon_tax_offset_usd = db.Column(db.Float, default=0.0)
    
    # Alpha Metrics
    gross_margin_pct = db.Column(db.Float)
    net_arbitrage_profit = db.Column(db.Float)
    
    confidence_score = db.Column(db.Float) # 0.0 to 1.0
    status = db.Column(db.String(20), default='IDENTIFIED') # IDENTIFIED, EXECUTING, CLOSED, INVALID
    
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'commodity': self.commodity_type,
            'buy_price': self.source_price_per_kg,
            'sell_price': self.target_price_per_kg,
            'net_profit': self.net_arbitrage_profit,
            'margin_pct': self.gross_margin_pct,
            'status': self.status
        }

class AlgorithmicTradeRecord(db.Model):
    """
    Executed algorithmic trades based on generated arbitrage matrix.
    """
    __tablename__ = 'algorithmic_trade_records'
    
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('arbitrage_opportunities.id'), nullable=False)
    
    execution_volume_kg = db.Column(db.Float, nullable=False)
    actual_buy_price = db.Column(db.Float)
    actual_sell_price = db.Column(db.Float)
    actual_transport_cost = db.Column(db.Float)
    
    realized_profit_usd = db.Column(db.Float)
    slippage_pct = db.Column(db.Float) # Expected vs actual price deviation
    
    ledger_txn_id = db.Column(db.Integer, db.ForeignKey('ledger_transactions.id'))
    
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime)
