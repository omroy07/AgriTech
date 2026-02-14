from backend.extensions import db
from backend.models.knowledge import UserExpertise, Badge, UserBadge
import json

class ReputationService:
    # Reputation points config
    POINTS = {
        'ask_question': 2,
        'give_answer': 5,
        'receive_question_vote': 10,
        'receive_answer_vote': 15,
        'answer_accepted': 50
    }

    @staticmethod
    def update_reputation(user_id, action_type):
        """Update user reputation score based on activity"""
        try:
            points = ReputationService.POINTS.get(action_type, 0)
            if points == 0:
                return
                
            # We track reputation per category or as a global score for MVP
            # Here we'll use a 'General' category for simplicity
            expertise = UserExpertise.query.filter_by(user_id=user_id, category='General').first()
            if not expertise:
                expertise = UserExpertise(user_id=user_id, category='General', reputation_score=0)
                db.session.add(expertise)
            
            expertise.reputation_score += points
            db.session.commit()
            
            # Check for new badges after reputation change
            ReputationService.check_and_award_badges(user_id, expertise.reputation_score)
            
        except Exception as e:
            print(f"Reputation update failed: {str(e)}")

    @staticmethod
    def check_and_award_badges(user_id, current_score):
        """Award badges based on reputation milestones"""
        milestones = [
            {'name': 'Novice Helper', 'score': 50, 'desc': 'Reached 50 reputation!'},
            {'name': 'Agri Expert', 'score': 500, 'desc': 'Reached 500 reputation!'},
            {'name': 'Farming Legend', 'score': 2000, 'desc': 'Reached 2000 reputation!'}
        ]
        
        for m in milestones:
            if current_score >= m['score']:
                # Find badge in DB or create it
                badge = Badge.query.filter_by(name=m['name']).first()
                if not badge:
                    badge = Badge(name=m['name'], description=m['desc'])
                    db.session.add(badge)
                    db.session.commit()
                
                # Check if user already has it
                has_badge = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
                if not has_badge:
                    user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
                    db.session.add(user_badge)
                    db.session.commit()
                    # Trigger notification (optional)

    @staticmethod
    def get_user_rankings(category='General', limit=10):
        """Get top users by reputation"""
        return UserExpertise.query.filter_by(category=category)\
            .order_by(UserExpertise.reputation_score.desc())\
            .limit(limit).all()
