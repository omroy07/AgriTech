from marshmallow import Schema, fields, validate

class WeatherSchema(Schema):
    id = fields.Int(dump_only=True)
    location = fields.Str(required=True)
    temperature = fields.Float(dump_only=True)
    humidity = fields.Float(dump_only=True)
    rainfall = fields.Float(dump_only=True)
    weather_condition = fields.Str(dump_only=True)
    timestamp = fields.DateTime(dump_only=True)

class AdvisorySubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    crop_name = fields.Str(required=True, validate=validate.Length(min=2))
    location = fields.Str(required=True)
    soil_type = fields.Str()
    sowing_date = fields.Date()
    frequency = fields.Str(validate=validate.OneOf(['Daily', 'Weekly']))

class CropAdvisorySchema(Schema):
    id = fields.Int(dump_only=True)
    crop_name = fields.Str(dump_only=True)
    advisory_text = fields.Str(dump_only=True)
    priority = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    is_read = fields.Bool()
    feedback_rating = fields.Int(validate=validate.Range(min=1, max=5))
