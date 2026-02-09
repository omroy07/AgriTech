from marshmallow import Schema, fields, validate

class CropPolicySchema(Schema):
    id = fields.Int(dump_only=True)
    farm_id = fields.Int(required=True)
    crop_type = fields.Str(required=True, validate=validate.OneOf(['Wheat', 'Rice', 'Coffee', 'Corn']))
    coverage = fields.Float(required=True, validate=validate.Range(min=100))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    premium = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)

class ClaimSchema(Schema):
    id = fields.Int(dump_only=True)
    policy_id = fields.Int(required=True)
    loss_kg = fields.Float(required=True, validate=validate.Range(min=1))
    reason = fields.Str(required=True, validate=validate.Length(min=10))
    evidence_url = fields.Url()
    claim_amount = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)

class AdjudicationSchema(Schema):
    decision = fields.Str(required=True, validate=validate.OneOf(['approve', 'reject']))
    notes = fields.Str(required=True, validate=validate.Length(min=5))
    verification_score = fields.Float(validate=validate.Range(min=0, max=1))
