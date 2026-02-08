from marshmallow import Schema, fields, validate

class EngineHourSchema(Schema):
    id = fields.Int(dump_only=True)
    equipment_id = fields.Int(required=True)
    booking_id = fields.Int()
    start = fields.Float(required=True, validate=validate.Range(min=0))
    end = fields.Float(required=True, validate=validate.Range(min=0))
    logged_at = fields.DateTime(dump_only=True)

class MaintenanceCycleSchema(Schema):
    id = fields.Int(dump_only=True)
    service_type = fields.Str(required=True, validate=validate.Length(min=3))
    interval = fields.Float(required=True, validate=validate.Range(min=10))
    status = fields.Str(dump_only=True)

class DamageReportSchema(Schema):
    id = fields.Int(dump_only=True)
    booking_id = fields.Int(required=True)
    equipment_id = fields.Int(required=True)
    description = fields.Str(required=True, validate=validate.Length(min=20))
    estimate = fields.Float(required=True, validate=validate.Range(min=0))
    reported_at = fields.DateTime(dump_only=True)
