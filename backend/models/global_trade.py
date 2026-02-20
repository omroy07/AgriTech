from datetime import datetime
from backend.extensions import db
from backend.models.procurement import BulkOrder
from backend.models.traceability import SupplyBatch

class CustomsManifest(db.Model):
    """
    Represents the official government declaration for cross-border export.
    Linked to a specific BulkOrder.
    """
    __tablename__ = 'customs_manifests'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('bulk_orders.id'), nullable=False)
    
    declaration_number = db.Column(db.String(50), unique=True, nullable=False)
    country_of_origin = db.Column(db.String(50), default='India')
    destination_country = db.Column(db.String(50), nullable=False)
    
    hs_code = db.Column(db.String(20)) # Harmonized System Code
    total_value_usd = db.Column(db.Float)
    
    # Status: DRAFT -> SUBMITTED -> UNDER_REVIEW -> CLEARED / REJECTED
    status = db.Column(db.String(20), default='DRAFT')
    
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cleared_at = db.Column(db.DateTime)
    
    # Documents
    phyto_cert_url = db.Column(db.String(255))
    commercial_invoice_url = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'declaration_ref': self.declaration_number,
            'destination': self.destination_country,
            'status': self.status,
            'cleared_at': self.cleared_at.isoformat() if self.cleared_at else None
        }

class ComplianceCheck(db.Model):
    """
    Recursive audit results for the "Seed-to-Shelf" history.
    """
    __tablename__ = 'compliance_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    manifest_id = db.Column(db.Integer, db.ForeignKey('customs_manifests.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id'), nullable=False)
    
    check_type = db.Column(db.String(50)) # PESTICIDE_RESIDUE, CHILD_LABOR, CARBON_FOOTPRINT
    passed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float) # 0-100
    
    details = db.Column(db.Text) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
