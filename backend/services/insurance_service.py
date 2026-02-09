from datetime import datetime
from backend.extensions import db
from backend.models.insurance_v2 import CropPolicy, ClaimRequest, PayoutLedger, AdjusterNote, PolicyStatus, ClaimStatus
from backend.utils.payout_calculator import PayoutCalculator
import uuid
import logging

logger = logging.getLogger(__name__)

class InsuranceService:
    @staticmethod
    def issue_policy(user_id, farm_id, crop_type, coverage, start_date, end_date):
        """Underwrite and issue a new crop insurance policy"""
        try:
            # 1. Calculate Risk (Mock regional hazard as 40)
            risk_score = PayoutCalculator.get_risk_assessment(crop_type, 40)
            
            # 2. Calculate Premium
            duration = (end_date - start_date).days
            premium = PayoutCalculator.calculate_premium(coverage, risk_score, duration)
            
            policy = CropPolicy(
                user_id=user_id,
                farm_id=farm_id,
                crop_type=crop_type,
                coverage_amount=coverage,
                premium_paid=premium,
                start_date=start_date,
                end_date=end_date,
                risk_score=risk_score,
                status=PolicyStatus.ACTIVE.value
            )
            
            db.session.add(policy)
            db.session.commit()
            return policy, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def file_claim(policy_id, loss_kg, reason, evidence_url=None):
        """Submit a new claim for loss assessment"""
        policy = CropPolicy.query.get(policy_id)
        if not policy:
            return None, "Policy not found"
            
        if policy.status != PolicyStatus.ACTIVE.value:
            return None, "Policy is not active"
            
        # Simplified: Expected yield is stored as coverage/10 (Mock)
        expected_yield = policy.coverage_amount / 10.0
        
        # Calculate suggested claim amount (cap at coverage)
        payout_ratio = PayoutCalculator.calculate_claim_eligibility(loss_kg, expected_yield, 0.5)
        suggested_payout = min(policy.coverage_amount, policy.coverage_amount * payout_ratio)
        
        claim = ClaimRequest(
            policy_id=policy_id,
            claim_amount=suggested_payout,
            reason=reason,
            evidence_url=evidence_url,
            status=ClaimStatus.SUBMITTED.value
        )
        
        db.session.add(claim)
        db.session.commit()
        return claim, None

    @staticmethod
    def process_claim(claim_id, adjuster_id, decision, notes, verification_score):
        """Finalize claim adjudication by an insurance adjuster"""
        claim = ClaimRequest.query.get(claim_id)
        if not claim:
            return False, "Claim not found"
            
        # 1. Log Adjuster Note
        note = AdjusterNote(
            claim_id=claim_id,
            adjuster_id=adjuster_id,
            content=notes,
            verification_score=verification_score
        )
        db.session.add(note)
        
        # 2. Update Status
        if decision == 'approve':
            claim.status = ClaimStatus.APPROVED.value
            # Trigger payout
            InsuranceService._execute_payout(claim)
        else:
            claim.status = ClaimStatus.REJECTED.value
            
        claim.processed_at = datetime.utcnow()
        db.session.commit()
        return True, None

    @staticmethod
    def _execute_payout(claim):
        """Simulate financial settlement for an approved claim"""
        payout = PayoutLedger(
            claim_id=claim.id,
            amount=claim.claim_amount,
            transaction_ref=f"PAY-{uuid.uuid4().hex[:12].upper()}"
        )
        claim.status = ClaimStatus.PAID.value
        db.session.add(payout)
        logger.info(f"Payout executed for Claim #{claim.id}: {claim.claim_amount} currency units.")
