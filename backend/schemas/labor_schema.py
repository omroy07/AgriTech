from marshmallow import Schema, fields, validate

class WorkerProfileSchema(Schema):
    id = fields.Int(dump_only=True)
    farm_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    worker_type = fields.Str(validate=validate.OneOf(['SEASONAL', 'PERMANENT']))
    hourly_rate = fields.Float(validate=validate.Range(min=0))
    piece_rate = fields.Float(validate=validate.Range(min=0))
    bank_details = fields.Str()

class AttendanceSchema(Schema):
    worker_id = fields.Int(required=True)
    break_mins = fields.Int(validate=validate.Range(min=0))

class HarvestLogSchema(Schema):
    worker_id = fields.Int(required=True)
    crop = fields.Str(required=True, validate=validate.Length(min=2))
    quantity = fields.Float(required=True, validate=validate.Range(min=0.1))

class PayrollRequestSchema(Schema):
    worker_id = fields.Int(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
