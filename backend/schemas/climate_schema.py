from marshmallow import Schema, fields, validate

class TelemetrySchema(Schema):
    temp = fields.Float(required=True, validate=validate.Range(min=-50, max=100))
    humidity = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    co2 = fields.Float(validate=validate.Range(min=0, max=10000))
    light = fields.Float(validate=validate.Range(min=0))
    battery = fields.Float(validate=validate.Range(min=0, max=100))
    rssi = fields.Float()

class ClimateZoneSchema(Schema):
    id = fields.Int(dump_only=True)
    farm_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str()
    temp_min = fields.Float()
    temp_max = fields.Float()
    hum_min = fields.Float()
    hum_max = fields.Float()
    co2_target = fields.Float()

class AutomationTriggerSchema(Schema):
    zone_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    actor = fields.Str(required=True, validate=validate.OneOf(['VENTILATION', 'IRRIGATION', 'LIGHTING', 'HEATING']))
    condition = fields.Dict(required=True)
    action = fields.Dict(required=True)
    enabled = fields.Bool()

class SensorNodeSchema(Schema):
    zone_id = fields.Int(required=True)
    uid = fields.Str(required=True)
    type = fields.Str()
    firmware = fields.Str()
