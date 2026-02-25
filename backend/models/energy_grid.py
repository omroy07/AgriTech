from datetime import datetime
import uuid
from backend.extensions import db

class DecentralizedEnergyGrid(db.Model):
    """
    A regional virtual power plant connecting multiple farms pushing tokenized renewable energy.
    """
    __tablename__ = 'decentralized_energy_grids'
    
    id = db.Column(db.Integer, primary_key=True)
    grid_name = db.Column(db.String(100), unique=True, nullable=False)
    region_code = db.Column(db.String(50))
    
    target_capacity_mwh = db.Column(db.Float, default=100.0)
    current_active_load_mwh = db.Column(db.Float, default=0.0)
    current_supply_mwh = db.Column(db.Float, default=0.0)
    
    # Real-time algorithmic pricing via supply/demand curve
    dynamic_feed_in_tariff_usd = db.Column(db.Float, default=0.10) # USD per kWh
    
    status = db.Column(db.String(20), default='OPERATIONAL') # OPERATIONAL, BROWNOUT, OVERLOAD
    last_rebalancing = db.Column(db.DateTime, default=datetime.utcnow)

class EnergyTokenMint(db.Model):
    """
    Tokenized representation of 1 MWh of clean energy injected into the grid by a Farm.
    Can be traded or retired against scope 2 emissions.
    """
    __tablename__ = 'energy_token_mints'
    
    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    grid_id = db.Column(db.Integer, db.ForeignKey('decentralized_energy_grids.id'), nullable=False)
    digester_log_id = db.Column(db.Integer, db.ForeignKey('biogas_digester_logs.id'))
    
    energy_mwh = db.Column(db.Float, nullable=False)
    mint_price_usd = db.Column(db.Float, nullable=False) # Valuation at the time of injection
    
    # Immutable ledger reference
    ledger_txn_id = db.Column(db.Integer, db.ForeignKey('ledger_transactions.id'))
    
    status = db.Column(db.String(20), default='MINTED') # MINTED, TRADED, RETIRED
    minted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'token_hash': self.token_hash,
            'farm_id': self.farm_id,
            'energy_mwh': self.energy_mwh,
            'mint_price_usd': self.mint_price_usd,
            'status': self.status,
            'minted_at': self.minted_at.isoformat()
        }

class GridInjectionLog(db.Model):
    """
    High frequency telemetry logging every kWh pushed to the grid.
    """
    __tablename__ = 'grid_injection_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    grid_id = db.Column(db.Integer, db.ForeignKey('decentralized_energy_grids.id'), nullable=False)
    
    kwh_injected = db.Column(db.Float, nullable=False)
    voltage_v = db.Column(db.Float)
    frequency_hz = db.Column(db.Float)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
