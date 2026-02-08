from marshmallow import Schema, fields, validate

class SensorLogSchema(Schema):
    id = fields.Int(dump_only=True)
    moisture = fields.Float(validate=validate.Range(min=0, max=100))
    temperature = fields.Float()
    ph_level = fields.Float(validate=validate.Range(min=0, max=14))
    timestamp = fields.DateTime(dump_only=True)

class IrrigationZoneSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str()
    moisture_threshold_min = fields.Float(validate=validate.Range(min=0, max=100))
    moisture_threshold_max = fields.Float(validate=validate.Range(min=0, max=100))
    status = fields.Str(dump_only=True)
    auto_mode = fields.Bool()

class IrrigationScheduleSchema(Schema):
    id = fields.Int(dump_only=True)
    start_time = fields.Time(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=1440))
    days_of_week = fields.Str(required=True, validate=validate.Regexp(r'^(mon|tue|wed|thu|fri|sat|sun)(,(mon|tue|wed|thu|fri|sat|sun))*$'))
    is_active = fields.Bool()
