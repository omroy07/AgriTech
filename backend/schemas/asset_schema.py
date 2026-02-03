"""
Marshmallow Validation Schemas for Asset & Logistics APIs
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class AssetCreateSchema(Schema):
    """Schema for creating a new farm asset."""
    asset_type = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    asset_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    manufacturer = fields.Str(allow_none=True, validate=validate.Length(max=100))
    model = fields.Str(allow_none=True, validate=validate.Length(max=100))
    serial_number = fields.Str(allow_none=True, validate=validate.Length(max=100))
    purchase_date = fields.Str(allow_none=True)  # ISO format
    purchase_price = fields.Float(allow_none=True, validate=validate.Range(min=0))
    alert_threshold_days = fields.Int(validate=validate.Range(min=1, max=90), missing=7)


class AssetUpdateSchema(Schema):
    """Schema for updating asset information."""
    asset_name = fields.Str(validate=validate.Length(min=1, max=200))
    status = fields.Str(validate=validate.OneOf(['ACTIVE', 'MAINTENANCE', 'FAILED', 'RETIRED']))
    alert_threshold_days = fields.Int(validate=validate.Range(min=1, max=90))


class TelemetrySchema(Schema):
    """Schema for asset telemetry data."""
    runtime_hours = fields.Float(validate=validate.Range(min=0), missing=0)
    temperature_c = fields.Float(allow_none=True)
    vibration_level = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    fuel_efficiency = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    error_codes = fields.List(fields.Str(), missing=[])
    oil_pressure = fields.Float(allow_none=True)
    battery_voltage = fields.Float(allow_none=True)
    engine_rpm = fields.Float(allow_none=True)
    custom_data = fields.Dict(allow_none=True)


class MaintenanceLogSchema(Schema):
    """Schema for logging maintenance activities."""
    maintenance_type = fields.Str(
        required=True,
        validate=validate.OneOf(['ROUTINE', 'REPAIR', 'EMERGENCY', 'INSPECTION'])
    )
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    parts_replaced = fields.List(fields.Str(), missing=[])
    cost = fields.Float(validate=validate.Range(min=0), missing=0)
    technician_name = fields.Str(allow_none=True, validate=validate.Length(max=200))
    technician_notes = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    scheduled_date = fields.Str(allow_none=True)  # ISO format
    status = fields.Str(
        validate=validate.OneOf(['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
        missing='SCHEDULED'
    )
    health_improvement = fields.Float(validate=validate.Range(min=0, max=30), missing=15)


class AssetQuerySchema(Schema):
    """Schema for asset query filters."""
    status = fields.Str(validate=validate.OneOf(['ACTIVE', 'MAINTENANCE', 'FAILED', 'RETIRED']))
    asset_type = fields.Str(validate=validate.Length(max=100))
    health_min = fields.Float(validate=validate.Range(min=0, max=100))
    health_max = fields.Float(validate=validate.Range(min=0, max=100))


class LogisticsOrderSchema(Schema):
    """Schema for creating a logistics order."""
    crop_type = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    quantity_tons = fields.Float(required=True, validate=validate.Range(min=0.1, max=100))
    pickup_location = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    pickup_latitude = fields.Float(allow_none=True, validate=validate.Range(min=-90, max=90))
    pickup_longitude = fields.Float(allow_none=True, validate=validate.Range(min=-180, max=180))
    destination_location = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    destination_latitude = fields.Float(allow_none=True, validate=validate.Range(min=-90, max=90))
    destination_longitude = fields.Float(allow_none=True, validate=validate.Range(min=-180, max=180))
    requested_pickup_date = fields.Str(required=True)  # ISO format
    priority = fields.Str(
        validate=validate.OneOf(['URGENT', 'HIGH', 'NORMAL', 'LOW']),
        missing='NORMAL'
    )
    special_instructions = fields.Str(allow_none=True, validate=validate.Length(max=500))
    requires_refrigeration = fields.Bool(missing=False)
    requires_covered_transport = fields.Bool(missing=False)
    
    @validates('requested_pickup_date')
    def validate_pickup_date(self, value):
        """Ensure pickup date is in the future."""
        try:
            pickup_date = datetime.fromisoformat(value)
            if pickup_date < datetime.utcnow():
                raise ValidationError('Pickup date must be in the future')
        except ValueError:
            raise ValidationError('Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)')


class VehicleAssignmentSchema(Schema):
    """Schema for assigning vehicle to route."""
    vehicle_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    driver_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    driver_phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    scheduled_pickup_date = fields.Str(required=True)  # ISO format
    
    @validates('scheduled_pickup_date')
    def validate_scheduled_date(self, value):
        """Validate ISO date format."""
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValidationError('Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)')
