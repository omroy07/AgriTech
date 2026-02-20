from datetime import datetime
from backend.extensions import db
from backend.models.sustainability import CarbonPractice, CreditLedger
from backend.utils.carbon_formulas import CarbonFormulas
import uuid
import logging

logger = logging.getLogger(__name__)

class CarbonService:
    @staticmethod
    def log_practice(user_id, farm_id, practice_type, area, start_date, description=None):
        """Register a new sustainable practice session"""
        try:
            practice = CarbonPractice(
                user_id=user_id,
                farm_id=farm_id,
                practice_type=practice_type,
                area_covered=area,
                start_date=start_date,
                description=description
            )
            db.session.add(practice)
            db.session.commit()
            return practice, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def calculate_and_update_offsets(practice_id):
        """Update the estimated offset based on elapsed time"""
        practice = CarbonPractice.query.get(practice_id)
        if not practice:
            return None
            
        end = practice.end_date or datetime.utcnow().date()
        duration = (end - practice.start_date).days
        
        offset = CarbonFormulas.calculate_offset(
            practice.practice_type, 
            practice.area_covered, 
            duration
        )
        
        practice.estimated_offset = offset
        db.session.commit()
        return offset

    @staticmethod
    def issue_credits(practice_id):
        """Convert verified offsets into tradeable ledger credits"""
        practice = CarbonPractice.query.get(practice_id)
        if not practice or not practice.is_verified:
            return None, "Practice must be verified before issuing credits"
            
        # 1 Credit = 1 Tonne CO2
        amount = practice.estimated_offset
        if amount <= 0:
            return None, "Offset value too low for credit issuance"
            
        credit = CreditLedger(
            owner_id=practice.user_id,
            practice_id=practice.id,
            amount=amount,
            serial_number=f"AGRI-{uuid.uuid4().hex[:12].upper()}"
        )
        
        db.session.add(credit)
        db.session.commit()
        return credit, None

    @staticmethod
    def get_user_impact(user_id):
        """Get summary of user's environmental impact"""
        practices = CarbonPractice.query.filter_by(user_id=user_id).all()
        total_offset = sum(p.estimated_offset for p in practices)
        credits_held = db.session.query(db.func.sum(CreditLedger.amount))\
            .filter_by(owner_id=user_id, status='Active').scalar() or 0
            
        return {
            'total_co2_offset': round(total_offset, 2),
            'active_credits': round(float(credits_held), 2),
            'practice_count': len(practices)
        }
