"""
Carbon Trading Escrow Models — L3-1642
=====================================
Smart-contract inspired escrow for carbon credit trades.
"""

from datetime import datetime
from backend.extensions import db

class CarbonTradeEscrow(db.Model):
    __tablename__ = 'carbon_trade_escrows'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    credits_volume = db.Column(db.Float, nullable=False)
    price_per_credit_usd = db.Column(db.Float, nullable=False)
    total_value_usd = db.Column(db.Float, nullable=False)
    
    # Escrow Status
    # LISTED -> FUNDED -> VERIFICATION -> RELEASED -> DISPUTED
    status = db.Column(db.String(20), default='LISTED')
    
    # Verification Hash (Satellite multi-spectral proof)
    verification_proof_hash = db.Column(db.String(128))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    ledger_txn_id = db.Column(db.Integer) # Reference to financial ledger

class EscrowAuditLog(db.Model):
    __tablename__ = 'carbon_escrow_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey('carbon_trade_escrows.id'), nullable=False)
    
    action = db.Column(db.String(50), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CarbonCreditWallet(db.Model):
    __tablename__ = 'carbon_credit_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    total_credits_minted = db.Column(db.Float, default=0.0)
    available_credits_for_sale = db.Column(db.Float, default=0.0)
    
    frozen_credits_in_escrow = db.Column(db.Float, default=0.0)
    last_rebalancing_at = db.Column(db.DateTime, default=datetime.utcnow)

