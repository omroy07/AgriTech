"""
Validation schemas for yield pool operations using marshmallow.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class CreatePoolSchema(Schema):
    """Schema for creating a new yield pool."""
    pool_name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    crop_type = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    target_quantity = fields.Float(required=True, validate=validate.Range(min=0.1))
    min_price_per_ton = fields.Float(required=True, validate=validate.Range(min=0.01))
    collection_location = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    logistics_overhead_percent = fields.Float(
        missing=5.0,
        validate=validate.Range(min=0, max=50)
    )
    
    @validates('target_quantity')
    def validate_target_quantity(self, value):
        if value > 10000:
            raise ValidationError("Target quantity cannot exceed 10,000 tons")


class AddContributionSchema(Schema):
    """Schema for adding a contribution to a pool."""
    pool_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity_tons = fields.Float(required=True, validate=validate.Range(min=0.01, max=1000))
    quality_grade = fields.Str(
        missing='A',
        validate=validate.OneOf(['A', 'B', 'C'])
    )
    
    @validates('quantity_tons')
    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError("Quantity must be positive")


class SetOfferSchema(Schema):
    """Schema for setting a buyer offer."""
    buyer_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    offer_price = fields.Float(required=True, validate=validate.Range(min=0.01))


class VoteSchema(Schema):
    """Schema for voting on a buyer offer."""
    vote = fields.Str(
        required=True,
        validate=validate.OneOf(['ACCEPT', 'REJECT'])
    )
    comment = fields.Str(validate=validate.Length(max=500))


class TransitionStateSchema(Schema):
    """Schema for transitioning pool state."""
    state = fields.Str(
        required=True,
        validate=validate.OneOf(['OPEN', 'LOCKED', 'COMPLETED', 'DISTRIBUTED'])
    )


class ShareResourceSchema(Schema):
    """Schema for sharing a resource with the pool."""
    resource_type = fields.Str(
        required=True,
        validate=validate.OneOf(['harvester', 'tractor', 'storage', 'transport', 'other'])
    )
    resource_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    resource_value = fields.Float(missing=0.0, validate=validate.Range(min=0))
    usage_cost_per_hour = fields.Float(missing=0.0, validate=validate.Range(min=0))
    is_free_for_pool = fields.Bool(missing=True)


class ROIComparisonSchema(Schema):
    """Schema for ROI comparison."""
    pool_id = fields.Int(required=True, validate=validate.Range(min=1))
    solo_price_per_ton = fields.Float(required=True, validate=validate.Range(min=0.01))


class EstimateValueSchema(Schema):
    """Schema for estimating contribution value."""
    pool_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity_tons = fields.Float(required=True, validate=validate.Range(min=0.01, max=1000))
