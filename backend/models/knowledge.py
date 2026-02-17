from datetime import datetime
from backend.extensions import db
import json

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), index=True) # e.g., 'Soil', 'Pests', 'Irrigation'
    
    view_count = db.Column(db.Integer, default=0)
    upvote_count = db.Column(db.Integer, default=0)
    answer_count = db.Column(db.Integer, default=0)
    
    is_closed = db.Column(db.Boolean, default=False)
    has_accepted_answer = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('KnowledgeVote', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'view_count': self.view_count,
            'upvote_count': self.upvote_count,
            'answer_count': self.answer_count,
            'is_closed': self.is_closed,
            'has_accepted_answer': self.has_accepted_answer,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username if hasattr(self, 'author') else 'Anonymous'
        }

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    upvote_count = db.Column(db.Integer, default=0)
    is_accepted = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    votes = db.relationship('KnowledgeVote', backref='answer', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'content': self.content,
            'upvote_count': self.upvote_count,
            'is_accepted': self.is_accepted,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username if hasattr(self, 'author') else 'Anonymous'
        }

class KnowledgeVote(db.Model):
    __tablename__ = 'knowledge_votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))
    
    vote_type = db.Column(db.Integer) # 1 for upvote, -1 for downvote (though we mostly use upvotes in this platform)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Badge(db.Model):
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    icon_url = db.Column(db.String(255))
    criteria_json = db.Column(db.Text) # JSON criteria for auto-awarding
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_url': self.icon_url
        }

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserExpertise(db.Model):
    __tablename__ = 'user_expertise'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    is_verified = db.Column(db.Boolean, default=False)
    verification_doc_url = db.Column(db.String(255))
    
    reputation_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
