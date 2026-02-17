from marshmallow import Schema, fields, validate

class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=10, max=255))
    content = fields.Str(required=True, validate=validate.Length(min=20))
    category = fields.Str(required=True)
    view_count = fields.Int(dump_only=True)
    upvote_count = fields.Int(dump_only=True)
    answer_count = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class AnswerSchema(Schema):
    id = fields.Int(dump_only=True)
    question_id = fields.Int(required=True)
    content = fields.Str(required=True, validate=validate.Length(min=10))
    upvote_count = fields.Int(dump_only=True)
    is_accepted = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class BadgeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    icon_url = fields.Str(dump_only=True)
