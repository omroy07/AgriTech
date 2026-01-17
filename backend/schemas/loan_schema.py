from marshmallow import Schema, fields, validate, pre_load
import re

class BaseSchema(Schema):
    @pre_load
    def sanitize_strings(self, data, **kwargs):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Remove HTML tags
                    clean = re.sub(r'<[^>]+>', '', value)
                    data[key] = clean.strip()
        return data

class LoanRequestSchema(BaseSchema):
    loan_type = fields.Str(required=True, validate=validate.OneOf([
        "Crop Cultivation", "Farm Equipment", "Water Resources", "Land Purchase", "Other"
    ]))
    amount = fields.Float(required=False)
    duration = fields.Int(required=False)
    purpose = fields.Str(required=False, validate=validate.Length(max=1000))
    # Allow additional fields since the prompt says they vary
    class Meta:
        include = { "additional": fields.Dict() }

class ChatRequestSchema(BaseSchema):
    message = fields.Str(required=False, validate=validate.Length(max=1000))
    image = fields.Str(required=False) # Base64 image string

class CropPredictionSchema(BaseSchema):
    N = fields.Float(required=True)
    P = fields.Float(required=True)
    K = fields.Float(required=True)
    temperature = fields.Float(required=True)
    humidity = fields.Float(required=True)
    ph = fields.Float(required=True)
    rainfall = fields.Float(required=True)
