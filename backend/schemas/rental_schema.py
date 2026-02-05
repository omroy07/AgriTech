from marshmallow import Schema, fields, validate, post_load
from datetime import datetime

class EquipmentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    category = fields.Str(required=True)
    description = fields.Str()
    hourly_rate = fields.Float(required=True, validate=validate.Range(min=0))
    daily_rate = fields.Float(required=True, validate=validate.Range(min=0))
    location = fields.Str(required=True)
    specifications = fields.Dict()
    is_available = fields.Bool(dump_only=True)

class BookingRequestSchema(Schema):
    equipment_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    
    @post_load
    def validate_dates(self, data, **kwargs):
        if data['start_time'] >= data['end_time']:
            from marshmallow import ValidationError
            raise ValidationError("End time must be after start time", "end_time")
        if data['start_time'] < datetime.utcnow():
            from marshmallow import ValidationError
            raise ValidationError("Start time cannot be in the past", "start_time")
        return data

class EscrowSchema(Schema):
    id = fields.Int(dump_only=True)
    booking_id = fields.Int(dump_only=True)
    total_amount = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    held_at = fields.DateTime(dump_only=True)
    released_at = fields.DateTime(dump_only=True)
    dispute_reason = fields.Str()
