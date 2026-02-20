from datetime import datetime
from backend.extensions import db

class WasteInventory(db.Model):
    __tablename__ = 'waste_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    waste_type = db.Column(db.String(100), nullable=False) # e.g., "Organic Bio-Mass", "Crop Residue", "Animal Waste"
    quantity_kg = db.Column(db.Float, default=0.0)
    
    # Status: PENDING_TRANSFORMATION, TRANSFORMED, UTILIZED_ON_FARM
    status = db.Column(db.String(50), default='PENDING_TRANSFORMATION')
    
    # Traceability for Circular Economy
    batch_source_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id')) # Link to the batch that generated waste
    is_reused_on_farm = db.Column(db.Boolean, default=False) # For Recursive Nutrient Recovery logic
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transformed_at = db.Column(db.DateTime)

class BioEnergyOutput(db.Model):
    __tablename__ = 'bio_energy_outputs'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    waste_id = db.Column(db.Integer, db.ForeignKey('waste_inventory.id'))
    
    energy_type = db.Column(db.String(50)) # "BIO_FUEL", "ELECTRICITY", "BIOGAS"
    amount_kwh = db.Column(db.Float)
    efficiency_ratio = db.Column(db.Float) # Transformation Efficiency
    
    carbon_offset_kg = db.Column(db.Float) # Calculated based on offset from fossil fuel
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CircularCredit(db.Model):
    __tablename__ = 'circular_credits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    credit_amount = db.Column(db.Float, default=0.0)
    source_type = db.Column(db.String(50)) # "RECYCLING", "ENERGY_GENERATION", "NUTRIENT_RECOVERY"
    
    # Metadata for audit
    audit_chain_hash = db.Column(db.String(64))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.credit_amount,
            'source': self.source_type,
            'created_at': self.created_at.isoformat()
        }
