from datetime import datetime, date
from backend.extensions import db

class WarehouseLocation(db.Model):
    __tablename__ = 'warehouse_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text)
    capacity = db.Column(db.Float) # in cubic meters or tons
    
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    stock_items = db.relationship('StockItem', backref='warehouse', lazy='dynamic')

class StockItem(db.Model):
    __tablename__ = 'stock_items'
    
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse_locations.id'), nullable=False)
    
    item_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50)) # Seeds, Fertilizers, Pesticides
    sku = db.Column(db.String(50), unique=True, nullable=False)
    
    current_quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20)) # kg, liters, bags
    
    reorder_point = db.Column(db.Float) # Trigger reorder when stock falls below this
    reorder_quantity = db.Column(db.Float) # Economic Order Quantity
    
    batch_number = db.Column(db.String(50))
    processing_batch_id = db.Column(db.Integer, db.ForeignKey('processing_batches.id'))
    supply_batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id'))
    
    base_price = db.Column(db.Float, default=0.0)
    current_market_price = db.Column(db.Float, default=0.0) # Adjusted by freshness
    freshness_score = db.Column(db.Float, default=100.0) # 0-100
    
    expiry_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    movements = db.relationship('StockMovement', backref='stock_item', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.item_name,
            'category': self.category,
            'sku': self.sku,
            'quantity': self.current_quantity,
            'unit': self.unit,
            'reorder_point': self.reorder_point,
            'batch': self.batch_number,
            'expiry': self.expiry_date.isoformat() if self.expiry_date else None
        }

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    
    movement_type = db.Column(db.String(20), nullable=False) # IN, OUT, ADJUSTMENT
    quantity = db.Column(db.Float, nullable=False)
    
    reference_doc = db.Column(db.String(100)) # PO number, Invoice, etc.
    reason = db.Column(db.Text)
    
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    movement_date = db.Column(db.DateTime, default=datetime.utcnow)

class ReconciliationLog(db.Model):
    __tablename__ = 'reconciliation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse_locations.id'), nullable=False)
    
    reconciliation_date = db.Column(db.Date, nullable=False, default=date.today)
    
    total_items_checked = db.Column(db.Integer)
    discrepancies_found = db.Column(db.Integer, default=0)
    shrinkage_value = db.Column(db.Float, default=0.0) # Value of missing stock
    
    notes = db.Column(db.Text)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
