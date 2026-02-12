from marshmallow import Schema, fields, validate

class DispatchRequestSchema(Schema):
    driver_id = fields.Int(required=True)
    vehicle_id = fields.Int(required=True)
    origin = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    destination = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    weight = fields.Float(required=True, validate=validate.Range(min=0.1))
    coords = fields.Dict(keys=fields.Str(), values=fields.List(fields.Float()))

class RouteUpdateSchema(Schema):
    actual_distance = fields.Float(required=True, validate=validate.Range(min=0.1))

class DriverProfileSchema(Schema):
    id = fields.Int(dump_only=True)
    license = fields.Str(required=True)
    phone = fields.Str()
    status = fields.Str(validate=validate.OneOf(['AVAILABLE', 'ON_TRIP', 'OFF_DUTY']))

class VehicleSchema(Schema):
    id = fields.Int(dump_only=True)
    plate = fields.Str(required=True)
    type = fields.Str()
    capacity = fields.Float(required=True)
    fuel_type = fields.Str()
