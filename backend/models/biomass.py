from datetime import datetime
from backend.extensions import db

class BiomassStockpile(db.Model):
    """
    Tracks raw crop residue and circular economy waste available for anaerobic digestion or combustion.
    """
    __tablename__ = 'biomass_stockpiles'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    stockpile_type = db.Column(db.String(50), nullable=False) # RICE_STRAW, MAIZE_STOVER, MANURE, WOOD_CHIPS
    total_mass_kg = db.Column(db.Float, default=0.0)
    
    moisture_content_pct = db.Column(db.Float) # Critical for combustion efficiency
    calorific_value_mj_per_kg = db.Column(db.Float) # Energy density
    
    # State tracking
    is_fermenting = db.Column(db.Boolean, default=False)
    methane_yield_potential_m3 = db.Column(db.Float, default=0.0) # Estimated Biogas
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'stockpile_type': self.stockpile_type,
            'mass_kg': self.total_mass_kg,
            'moisture_pct': self.moisture_content_pct,
            'energy_density_mj': self.calorific_value_mj_per_kg,
            'methane_potential': self.methane_yield_potential_m3
        }

class BiogasDigesterLog(db.Model):
    """
    Lifecycle of anaerobic digestion turning BiomassStockpile into Methane / Energy.
    """
    __tablename__ = 'biogas_digester_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    stockpile_id = db.Column(db.Integer, db.ForeignKey('biomass_stockpiles.id'), nullable=False)
    
    mass_consumed_kg = db.Column(db.Float, nullable=False)
    digestion_temp_c = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    
    methane_produced_m3 = db.Column(db.Float, default=0.0)
    electricity_generated_kwh = db.Column(db.Float, default=0.0) # Converted via CHP
    
    status = db.Column(db.String(20), default='ACTIVE') # ACTIVE, COMPLETED, FAILED
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'stockpile_id': self.stockpile_id,
            'consumed_kg': self.mass_consumed_kg,
            'methane_m3': self.methane_produced_m3,
            'electricity_kwh': self.electricity_generated_kwh,
            'status': self.status
        }
