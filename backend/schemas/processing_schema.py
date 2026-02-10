from marshmallow import Schema, fields, validate

class ProcessingBatchSchema(Schema):
    id = fields.Int(dump_only=True)
    batch_number = fields.Str(dump_only=True)
    product_type = fields.Str(required=True)
    total_weight = fields.Float(required=True, validate=validate.Range(min=0.1))
    current_weight = fields.Float(dump_only=True)
    current_stage = fields.Str(dump_only=True)
    origin_farms = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class AuditSchema(Schema):
    moisture = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    purity = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    weight = fields.Float(required=True, validate=validate.Range(min=0))
    comments = fields.Str()

class AdvanceStageSchema(Schema):
    next_stage = fields.Str(required=True, validate=validate.OneOf([
        'cleaning', 'processing', 'grading', 'packaging', 'completed'
    ]))
