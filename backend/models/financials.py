from datetime import datetime
from backend.extensions import db

class FarmBalanceSheet(db.Model):
    __tablename__ = 'farm_balance_sheets'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    # Assets
    cash_on_hand = db.Column(db.Float, default=0.0)
    inventory_value = db.Column(db.Float, default=0.0)
    fixed_assets_value = db.Column(db.Float, default=0.0)
    
    # Liabilities
    outstanding_loans = db.Column(db.Float, default=0.0)
    accounts_payable = db.Column(db.Float, default=0.0)
    
    # Equity
    net_worth = db.Column(db.Float, default=0.0)
    
    period_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'cash': self.cash_on_hand,
            'inventory': self.inventory_value,
            'fixed_assets': self.fixed_assets_value,
            'loans': self.outstanding_loans,
            'payable': self.accounts_payable,
            'net_worth': self.net_worth,
            'date': self.period_date.isoformat()
        }

class ProfitabilityIndex(db.Model):
    __tablename__ = 'profitability_indices'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    roi_machinery = db.Column(db.Float, default=0.0)
    roi_labor = db.Column(db.Float, default=0.0)
    yield_efficiency = db.Column(db.Float, default=0.0) # Actual vs Predicted
    
    overall_profitability_score = db.Column(db.Float, default=0.0)
    
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

class SolvencySnapshot(db.Model):
    __tablename__ = 'solvency_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    debt_to_equity_ratio = db.Column(db.Float, default=0.0)
    liquidity_ratio = db.Column(db.Float, default=0.0)
    bankruptcy_risk_score = db.Column(db.Float, default=0.0) # 0-100
    
    # Status: HEALTHY, WARNING, CRITICAL, INSOLVENT
    status = db.Column(db.String(20), default='HEALTHY')
    
    next_review_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'debt_to_equity': self.debt_to_equity_ratio,
            'liquidity': self.liquidity_ratio,
            'risk_score': self.bankruptcy_risk_score,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
