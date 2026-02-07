from datetime import datetime
from backend.extensions import db
from backend.models.knowledge import Question, Answer, KnowledgeVote, UserExpertise
from backend.services.reputation_service import ReputationService
import logging

logger = logging.getLogger(__name__)

class KnowledgeService:
    @staticmethod
    def create_question(user_id, title, content, category):
        """Create a new farming question"""
        try:
            question = Question(
                user_id=user_id,
                title=title,
                content=content,
                category=category
            )
            db.session.add(question)
            db.session.commit()
            
            # Award reputation for asking
            ReputationService.update_reputation(user_id, 'ask_question')
            
            return question, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_questions(category=None, search=None, sort='newest'):
        """Query questions with filters and sorting"""
        query = Question.query
        
        if category:
            query = query.filter(Question.category == category)
            
        if search:
            query = query.filter(
                (Question.title.ilike(f"%{search}%")) | 
                (Question.content.ilike(f"%{search}%"))
            )
            
        if sort == 'popular':
            query = query.order_by(Question.upvote_count.desc())
        elif sort == 'trending':
            # Simplified trending: high views + votes in recent time
            query = query.order_by((Question.view_count + Question.upvote_count * 5).desc())
        else:
            query = query.order_by(Question.created_at.desc())
            
        return query.limit(50).all()

    @staticmethod
    def add_answer(question_id, user_id, content):
        """Add an answer to a question"""
        try:
            question = Question.query.get(question_id)
            if not question:
                return None, "Question not found"
                
            answer = Answer(
                question_id=question_id,
                user_id=user_id,
                content=content
            )
            db.session.add(answer)
            
            # Increment answer count
            question.answer_count += 1
            
            db.session.commit()
            
            # Award reputation for answering
            ReputationService.update_reputation(user_id, 'give_answer')
            
            return answer, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def vote_item(user_id, item_type, item_id):
        """Vote on a question or answer"""
        try:
            if item_type == 'question':
                item = Question.query.get(item_id)
                vote_filter = {'user_id': user_id, 'question_id': item_id}
            else:
                item = Answer.query.get(item_id)
                vote_filter = {'user_id': user_id, 'answer_id': item_id}
                
            if not item:
                return False, f"{item_type.capitalize()} not found"
                
            existing_vote = KnowledgeVote.query.filter_by(**vote_filter).first()
            if existing_vote:
                return False, "Already voted"
                
            # Create vote
            vote = KnowledgeVote(user_id=user_id, **vote_filter, vote_type=1)
            db.session.add(vote)
            
            # Update count
            item.upvote_count += 1
            
            # Award reputation to author
            ReputationService.update_reputation(item.user_id, f'receive_{item_type}_vote')
            
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def accept_answer(user_id, answer_id):
        """Mark an answer as accepted (by question author)"""
        try:
            answer = Answer.query.get(answer_id)
            if not answer:
                return False, "Answer not found"
                
            question = Question.query.get(answer.question_id)
            if question.user_id != user_id:
                return False, "Only author can accept answer"
                
            if question.has_accepted_answer:
                return False, "Already has an accepted answer"
                
            answer.is_accepted = True
            question.has_accepted_answer = True
            
            # Large reputation bonus for accepted answer
            ReputationService.update_reputation(answer.user_id, 'answer_accepted')
            
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
