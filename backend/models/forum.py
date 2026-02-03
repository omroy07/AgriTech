"""
Community Forum models for discussions, comments, and reputation.
"""
from backend.extensions import db
from datetime import datetime


class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    threads = db.relationship('ForumThread', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'thread_count': len(self.threads)
        }


class ForumThread(db.Model):
    __tablename__ = 'forum_threads'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255))  # Comma-separated tags
    
    # Status and flags
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(255))
    
    # AI Moderation
    sentiment_score = db.Column(db.Float)  # -1.0 to 1.0
    toxicity_score = db.Column(db.Float)   # 0.0 to 1.0
    is_ai_approved = db.Column(db.Boolean, default=True)
    
    # Engagement metrics
    view_count = db.Column(db.Integer, default=0)
    upvote_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('PostComment', backref='thread', lazy=True, cascade='all, delete-orphan')
    upvotes = db.relationship('Upvote', backref='thread', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_comments=False):
        data = {
            'id': self.id,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags.split(',') if self.tags else [],
            'is_pinned': self.is_pinned,
            'is_locked': self.is_locked,
            'is_flagged': self.is_flagged,
            'view_count': self.view_count,
            'upvote_count': self.upvote_count,
            'comment_count': len(self.comments),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }
        if include_comments:
            data['comments'] = [c.to_dict() for c in self.comments]
        return data
    
    def __repr__(self):
        return f'<ForumThread {self.id} - {self.title[:50]}>'


class PostComment(db.Model):
    __tablename__ = 'post_comments'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('forum_threads.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comments.id'), nullable=True)  # For nested replies
    
    content = db.Column(db.Text, nullable=False)
    
    # AI Moderation
    sentiment_score = db.Column(db.Float)
    is_ai_approved = db.Column(db.Boolean, default=True)
    is_ai_generated = db.Column(db.Boolean, default=False)  # For auto-answers
    
    # Status
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(255))
    
    # Engagement
    upvote_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('PostComment', backref=db.backref('parent', remote_side=[id]), lazy=True, cascade='all, delete-orphan')
    upvotes = db.relationship('Upvote', backref='comment', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_replies=True):
        data = {
            'id': self.id,
            'thread_id': self.thread_id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'is_ai_generated': self.is_ai_generated,
            'is_flagged': self.is_flagged,
            'upvote_count': self.upvote_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_replies and self.replies:
            data['replies'] = [r.to_dict(include_replies=False) for r in self.replies]
        return data
    
    def __repr__(self):
        return f'<PostComment {self.id} on Thread {self.thread_id}>'


class Upvote(db.Model):
    __tablename__ = 'upvotes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('forum_threads.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('post_comments.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a user can only upvote once per thread or comment
    __table_args__ = (
        db.CheckConstraint('(thread_id IS NOT NULL AND comment_id IS NULL) OR (thread_id IS NULL AND comment_id IS NOT NULL)'),
        db.UniqueConstraint('user_id', 'thread_id', name='unique_thread_upvote'),
        db.UniqueConstraint('user_id', 'comment_id', name='unique_comment_upvote')
    )
    
    def __repr__(self):
        return f'<Upvote by User {self.user_id}>'


class UserReputation(db.Model):
    __tablename__ = 'user_reputations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Reputation metrics
    total_score = db.Column(db.Integer, default=0)
    threads_created = db.Column(db.Integer, default=0)
    comments_posted = db.Column(db.Integer, default=0)
    upvotes_received = db.Column(db.Integer, default=0)
    helpful_answers = db.Column(db.Integer, default=0)  # Comments marked as "solution"
    
    # Badges
    is_expert = db.Column(db.Boolean, default=False)
    is_moderator = db.Column(db.Boolean, default=False)
    badges = db.Column(db.Text)  # JSON string of earned badges
    
    # Timestamps
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_score(self):
        """Calculate total reputation score based on activity"""
        self.total_score = (
            (self.threads_created * 5) +
            (self.comments_posted * 2) +
            (self.upvotes_received * 10) +
            (self.helpful_answers * 50)
        )
        
        # Grant expert badge if score > 500
        if self.total_score >= 500:
            self.is_expert = True
        
        return self.total_score
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total_score': self.total_score,
            'threads_created': self.threads_created,
            'comments_posted': self.comments_posted,
            'upvotes_received': self.upvotes_received,
            'helpful_answers': self.helpful_answers,
            'is_expert': self.is_expert,
            'is_moderator': self.is_moderator,
            'badges': self.badges
        }
    
    def __repr__(self):
        return f'<UserReputation User {self.user_id} - Score: {self.total_score}>'
