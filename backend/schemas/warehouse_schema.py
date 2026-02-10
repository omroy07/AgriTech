from marshmallow import Schema, fields, validate

class StockItemSchema(Schema):
    id = fields.Int(dump_only=True)
    warehouse_id = fields.Int(required=True)
    item_name = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    category = fields.Str(validate=validate.OneOf(['Seeds', 'Fertilizers', 'Pesticides', 'Equipment']))
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    quantity = fields.Float(validate=validate.Range(min=0))
    unit = fields.Str(validate=validate.OneOf(['kg', 'liters', 'bags', 'units']))
    reorder_point = fields.Float(validate=validate.Range(min=0))
    batch_number = fields.Str()
    expiry_date = fields.Date()

class StockMovementSchema(Schema):
    stock_item_id = fields.Int(required=True)
    quantity = fields.Float(required=True, validate=validate.Range(min=0.01))
    reference = fields.Str(validate=validate.Length(max=100))
    reason = fields.Str()

class ReconciliationSchema(Schema):
    warehouse_id = fields.Int(required=True)
    physical_counts = fields.Dict(required=True)
    notes = fields.Str()
