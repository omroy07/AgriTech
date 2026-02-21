from datetime import datetime
from backend.extensions import db

class CarbonPractice(db.Model):
    __tablename__ = 'carbon_practices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    carbon_offset_per_unit = db.Column(db.Float)

class CreditLedger(db.Model):
    __tablename__ = 'credit_ledger'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    credits_earned = db.Column(db.Float, default=0.0)
    credits_spent = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuditRequest(db.Model):
    __tablename__ = 'sustainability_audits'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# New Models (L3-1558)
class CarbonLedger(db.Model):
    __tablename__ = 'carbon_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id')) # Optional, can be farm-level
    
    # Emission Data (kg CO2e)
    scope_1_direct = db.Column(db.Float, default=0.0) # On-farm fuel, soil N2O
    scope_2_indirect = db.Column(db.Float, default=0.0) # Purchased electricity (irrigation)
    scope_3_supply_chain = db.Column(db.Float, default=0.0) # Fertilizer/Seed production
    
    total_footprint = db.Column(db.Float, default=0.0)
    sequestration_offset = db.Column(db.Float, default=0.0) # Tree planting, etc.
    
    net_carbon_balance = db.Column(db.Float, default=0.0)
    certification_status = db.Column(db.String(50), default='PENDING') # PENDING, CARBON_NEUTRAL, NET_ZERO
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'scope_1': self.scope_1_direct,
            'scope_2': self.scope_2_indirect,
            'scope_3': self.scope_3_supply_chain,
            'net_balance': self.net_carbon_balance,
            'status': self.certification_status,
            'date': self.recorded_at.isoformat()
        }

class EmissionSource(db.Model):
    __tablename__ = 'emission_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    ledger_id = db.Column(db.Integer, db.ForeignKey('carbon_ledger.id'), nullable=False)
    
    source_type = db.Column(db.String(50)) # FUEL, FERTILIZER, WATER, TRANSPORT
    ref_id = db.Column(db.Integer) # ID of the source record (e.g. FuelLog.id)
    
    emission_value = db.Column(db.Float, nullable=False) # kg CO2e
    calculation_method = db.Column(db.String(100))
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SustainabilityScore(db.Model):
    __tablename__ = 'sustainability_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    carbon_efficiency = db.Column(db.Float) # kg CO2e per kg yield
    water_efficiency = db.Column(db.Float) # Liters per kg yield
    biodiversity_index = db.Column(db.Float)
    
    overall_rating = db.Column(db.Float) # 0-100
    
    # Bonus from Bio-Mass & Waste Recovery (L3-1594)
    circular_economy_bonus = db.Column(db.Float, default=0.0)
    
    # Offset points for Barter Arbitrage
    offset_credits_available = db.Column(db.Float, default=0.0)
    
    # Water Scarcity Tracking (L3-1605)
    water_quota_utilization_ratio = db.Column(db.Float, default=0.0) # used / total
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
