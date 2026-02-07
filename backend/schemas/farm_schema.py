from marshmallow import Schema, fields, validate

class FarmSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    location = fields.Str(required=True)
    acreage = fields.Float(validate=validate.Range(min=0))
    description = fields.Str()
    soil_details = fields.Dict()
    created_at = fields.DateTime(dump_only=True)

class FarmMemberSchema(Schema):
    id = fields.Int(dump_only=True)
    farm_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    role = fields.Str(validate=validate.OneOf(['owner', 'manager', 'worker', 'viewer']))
    joined_at = fields.DateTime(dump_only=True)

class FarmAssetSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    purchase_value = fields.Float(validate=validate.Range(min=0))
    current_valuation = fields.Float(dump_only=True)
    condition = fields.Str(validate=validate.OneOf(['Good', 'Needs Repair', 'Critical']))
    last_maintenance = fields.DateTime(dump_only=True)
