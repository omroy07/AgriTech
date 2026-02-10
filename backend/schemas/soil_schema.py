from marshmallow import Schema, fields, validate

class SoilTestSchema(Schema):
    id = fields.Int(dump_only=True)
    farm_id = fields.Int(required=True)
    nitrogen = fields.Float(required=True, validate=validate.Range(min=0))
    phosphorus = fields.Float(required=True, validate=validate.Range(min=0))
    potassium = fields.Float(required=True, validate=validate.Range(min=0))
    ph_level = fields.Float(required=True, validate=validate.Range(min=0, max=14))
    organic_matter = fields.Float(validate=validate.Range(min=0, max=100))
    ec = fields.Float(validate=validate.Range(min=0))
    lab_name = fields.Str(validate=validate.Length(max=150))
    report_url = fields.Url(validate=validate.Length(max=255))
    test_date = fields.Date()

class RecommendationSchema(Schema):
    id = fields.Int(dump_only=True)
    crop_type = fields.Str(dump_only=True)
    nitrogen = fields.Float(dump_only=True)
    phosphorus = fields.Float(dump_only=True)
    potassium = fields.Float(dump_only=True)
    lime = fields.Float(dump_only=True)
    suggestions = fields.List(fields.Dict(), dump_only=True)

class FertilizerApplicationSchema(Schema):
    test_id = fields.Int(required=True)
    fertilizer_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    amount = fields.Float(required=True, validate=validate.Range(min=0.1))
    area = fields.Float(required=True, validate=validate.Range(min=0.01))
    notes = fields.Str()
