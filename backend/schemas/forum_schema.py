from marshmallow import Schema, fields, validates, ValidationError, validate
import re


class ForumCategorySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    icon = fields.Str(validate=validate.Length(max=50))


class ForumThreadCreateSchema(Schema):
    category_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=5, max=255))
    content = fields.Str(required=True, validate=validate.Length(min=10, max=10000))
    tags = fields.List(fields.Str(validate=validate.Length(max=50)), validate=validate.Length(max=10))
    
    @validates('title')
    def validate_title(self, value):
        """Ensure title doesn't contain only special characters"""
        if not re.search(r'[a-zA-Z0-9]', value):
            raise ValidationError("Title must contain at least some alphanumeric characters")
        
        # Check for spam patterns
        spam_patterns = [
            r'(click here|buy now|limited offer)',
            r'(http://|https://|www\.)',
            r'(\d{10,})',  # Long numbers (spam phone numbers)
        ]
        for pattern in spam_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValidationError("Title appears to contain spam or promotional content")
    
    @validates('content')
    def validate_content(self, value):
        """Validate content for basic quality"""
        if len(value.strip()) < 10:
            raise ValidationError("Content is too short. Please provide more details.")
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in value if c.isupper()) / len(value)
        if caps_ratio > 0.5:
            raise ValidationError("Please avoid excessive use of capital letters")


class PostCommentCreateSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    parent_id = fields.Int(allow_none=True)
    
    @validates('content')
    def validate_content(self, value):
        """Validate comment content"""
        if value.strip() == '':
            raise ValidationError("Comment cannot be empty")
        
        # Detect URL spam
        url_count = len(re.findall(r'http[s]?://\S+', value))
        if url_count > 2:
            raise ValidationError("Too many links in comment. Maximum 2 links allowed.")


class ThreadSearchSchema(Schema):
    q = fields.Str(validate=validate.Length(max=200))
    category_id = fields.Int()
    tags = fields.Str(validate=validate.Length(max=200))
    sort_by = fields.Str(validate=validate.OneOf(['relevance', 'recent', 'popular', 'unanswered']))
    limit = fields.Int(validate=validate.Range(min=1, max=100))


class FlagContentSchema(Schema):
    thread_id = fields.Int()
    comment_id = fields.Int()
    reason = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    
    @validates('reason')
    def validate_reason(self, value):
        """Ensure flag reason is meaningful"""
        if len(value.strip()) < 5:
            raise ValidationError("Please provide a detailed reason for flagging")


class MarkSolutionSchema(Schema):
    comment_id = fields.Int(required=True)


class UpdateThreadSchema(Schema):
    title = fields.Str(validate=validate.Length(min=5, max=255))
    content = fields.Str(validate=validate.Length(min=10, max=10000))
    tags = fields.List(fields.Str(validate=validate.Length(max=50)))
    is_pinned = fields.Bool()
    is_locked = fields.Bool()
