"""
Insurance service for policy management and claim processing.
Handles policy issuance, renewals, claims, and risk-based underwriting.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import random
import string
from sqlalchemy import and_, or_

from backend.models import (
    db, User, InsurancePolicy, ClaimRequest, RiskScoreHistory
)
from backend.services.risk_service import RiskService
from backend.utils.risk_calculators import RiskCalculators


class InsuranceService:
    """Service for agricultural insurance operations."""
    
    @staticmethod
    def create_policy(
        user_id: int,
        coverage_amount: float,
        crop_type: str,
        farm_location: str,
        farm_size: float,
        coverage_months: int = 6
    ) -> Dict:
        """
        Create a new insurance policy with automated underwriting.
        
        Args:
            user_id: User ID
            coverage_amount: Desired coverage amount
            crop_type: Type of crop
            farm_location: Farm location details
            farm_size: Farm size in acres
            coverage_months: Coverage period in months
            
        Returns:
            dict: Created policy details
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Calculate risk score
        risk_data = RiskService.calculate_user_risk_score(user_id)
        ars_score = risk_data['ars_score']
        
        # Calculate premium
        premium, base_rate, risk_multiplier = RiskCalculators.calculate_premium(
            coverage_amount=coverage_amount,
            crop_type=crop_type,
            ars_score=ars_score,
            farm_size_acres=farm_size
        )
        
        # Generate unique policy number
        policy_number = InsuranceService._generate_policy_number()
        
        # Calculate dates
        issue_date = datetime.utcnow()
        start_date = issue_date
        end_date = start_date + timedelta(days=coverage_months * 30)
        
        # Create policy
        policy = InsurancePolicy(
            user_id=user_id,
            policy_number=policy_number,
            coverage_amount=Decimal(str(coverage_amount)),
            premium_amount=Decimal(str(premium)),
            ars_score_at_issuance=ars_score,
            risk_multiplier=risk_multiplier,
            crop_type=crop_type,
            farm_location=farm_location,
            farm_size_acres=farm_size,
            issue_date=issue_date,
            start_date=start_date,
            end_date=end_date,
            status='ACTIVE'
        )
        
        db.session.add(policy)
        db.session.commit()
        
        return {
            'policy_id': policy.id,
            'policy_number': policy.policy_number,
            'coverage_amount': float(policy.coverage_amount),
            'premium_amount': float(policy.premium_amount),
            'ars_score': ars_score,
            'risk_category': risk_data['risk_category'],
            'risk_multiplier': risk_multiplier,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'status': 'ACTIVE',
            'message': 'Policy created successfully'
        }
    
    @staticmethod
    def _generate_policy_number() -> str:
        """Generate unique policy number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"AIP-{timestamp}-{random_part}"
    
    @staticmethod
    def _generate_claim_number() -> str:
        """Generate unique claim number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"CLM-{timestamp}-{random_part}"
    
    @staticmethod
    def get_user_policies(
        user_id: int,
        status: Optional[str] = None,
        active_only: bool = False
    ) -> List[Dict]:
        """
        Get all policies for a user.
        
        Args:
            user_id: User ID
            status: Filter by status (ACTIVE, EXPIRED, CANCELLED, CLAIMED)
            active_only: Only return active policies
            
        Returns:
            list: Policy records
        """
        query = InsurancePolicy.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter(
                and_(
                    InsurancePolicy.status == 'ACTIVE',
                    InsurancePolicy.end_date > datetime.utcnow()
                )
            )
        elif status:
            query = query.filter_by(status=status)
        
        policies = query.order_by(InsurancePolicy.created_at.desc()).all()
        return [policy.to_dict() for policy in policies]
    
    @staticmethod
    def get_policy_details(policy_id: int) -> Dict:
        """Get detailed policy information."""
        policy = InsurancePolicy.query.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        policy_dict = policy.to_dict()
        
        # Add claims information
        claims = ClaimRequest.query.filter_by(policy_id=policy_id)\
            .order_by(ClaimRequest.created_at.desc())\
            .all()
        policy_dict['claims'] = [claim.to_dict() for claim in claims]
        policy_dict['claims_count'] = len(claims)
        
        # Check if policy is expiring soon
        days_until_expiry = (policy.end_date - datetime.utcnow()).days
        policy_dict['days_until_expiry'] = days_until_expiry
        policy_dict['renewal_recommended'] = days_until_expiry <= 30
        
        return policy_dict
    
    @staticmethod
    def renew_policy(
        policy_id: int,
        coverage_months: int = 6,
        adjust_coverage: Optional[float] = None
    ) -> Dict:
        """
        Renew an existing policy.
        
        Args:
            policy_id: Policy ID to renew
            coverage_months: Coverage period for renewal
            adjust_coverage: Optional new coverage amount
            
        Returns:
            dict: New policy details
        """
        old_policy = InsurancePolicy.query.get(policy_id)
        if not old_policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        # Use existing coverage or adjusted amount
        coverage_amount = adjust_coverage if adjust_coverage else float(old_policy.coverage_amount)
        
        # Create new policy with recalculated risk score
        new_policy = InsuranceService.create_policy(
            user_id=old_policy.user_id,
            coverage_amount=coverage_amount,
            crop_type=old_policy.crop_type,
            farm_location=old_policy.farm_location,
            farm_size=old_policy.farm_size_acres,
            coverage_months=coverage_months
        )
        
        # Mark old policy as expired if still active
        if old_policy.status == 'ACTIVE':
            old_policy.status = 'EXPIRED'
            db.session.commit()
        
        new_policy['previous_policy'] = old_policy.policy_number
        new_policy['message'] = 'Policy renewed successfully'
        
        return new_policy
    
    @staticmethod
    def cancel_policy(policy_id: int, reason: str) -> Dict:
        """Cancel an active policy."""
        policy = InsurancePolicy.query.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        if policy.status != 'ACTIVE':
            raise ValueError(f"Cannot cancel policy with status {policy.status}")
        
        policy.status = 'CANCELLED'
        policy.notes = f"Cancelled: {reason}"
        db.session.commit()
        
        return {
            'policy_id': policy.id,
            'policy_number': policy.policy_number,
            'status': 'CANCELLED',
            'message': 'Policy cancelled successfully'
        }
    
    @staticmethod
    def submit_claim(
        policy_id: int,
        claimed_amount: float,
        incident_date: datetime,
        incident_description: str,
        evidence_photos: List[str] = None
    ) -> Dict:
        """
        Submit an insurance claim.
        
        Args:
            policy_id: Policy ID
            claimed_amount: Amount claimed
            incident_date: Date of incident
            incident_description: Description of loss/damage
            evidence_photos: List of photo URLs
            
        Returns:
            dict: Claim details
        """
        policy = InsurancePolicy.query.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        # Validate policy status
        if policy.status != 'ACTIVE':
            raise ValueError(f"Cannot claim on policy with status {policy.status}")
        
        # Validate incident date is within coverage period
        if incident_date < policy.start_date or incident_date > policy.end_date:
            raise ValueError("Incident date is outside policy coverage period")
        
        # Validate claimed amount
        if claimed_amount > float(policy.coverage_amount):
            raise ValueError(f"Claimed amount exceeds coverage amount")
        
        # Generate claim number
        claim_number = InsuranceService._generate_claim_number()
        
        # Create claim
        claim = ClaimRequest(
            policy_id=policy_id,
            user_id=policy.user_id,
            claim_number=claim_number,
            claimed_amount=Decimal(str(claimed_amount)),
            incident_date=incident_date,
            incident_description=incident_description,
            evidence_photos=evidence_photos or [],
            status='SUBMITTED',
            ai_verification_status='PENDING'
        )
        
        db.session.add(claim)
        db.session.commit()
        
        # TODO: Trigger async AI verification task
        # from backend.tasks import verify_claim_with_ai_task
        # verify_claim_with_ai_task.delay(claim.id)
        
        return {
            'claim_id': claim.id,
            'claim_number': claim.claim_number,
            'policy_number': policy.policy_number,
            'claimed_amount': float(claim.claimed_amount),
            'status': 'SUBMITTED',
            'message': 'Claim submitted successfully. AI verification in progress.'
        }
    
    @staticmethod
    def get_user_claims(user_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get all claims for a user."""
        query = ClaimRequest.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        claims = query.order_by(ClaimRequest.created_at.desc()).all()
        
        # Enrich with policy details
        result = []
        for claim in claims:
            claim_dict = claim.to_dict()
            policy = InsurancePolicy.query.get(claim.policy_id)
            claim_dict['policy_number'] = policy.policy_number if policy else None
            result.append(claim_dict)
        
        return result
    
    @staticmethod
    def process_claim_decision(
        claim_id: int,
        decision: str,
        approved_amount: Optional[float] = None,
        rejection_reason: Optional[str] = None,
        processed_by: int = None
    ) -> Dict:
        """
        Process claim approval or rejection (admin function).
        
        Args:
            claim_id: Claim ID
            decision: 'APPROVED' or 'REJECTED'
            approved_amount: Approved amount (if approved)
            rejection_reason: Reason for rejection
            processed_by: Admin user ID
            
        Returns:
            dict: Updated claim details
        """
        claim = ClaimRequest.query.get(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        
        if claim.status not in ['SUBMITTED', 'UNDER_REVIEW']:
            raise ValueError(f"Cannot process claim with status {claim.status}")
        
        if decision == 'APPROVED':
            if not approved_amount:
                approved_amount = float(claim.claimed_amount)
            
            claim.status = 'APPROVED'
            claim.approved_amount = Decimal(str(approved_amount))
            claim.processed_at = datetime.utcnow()
            
            # Update policy status
            policy = InsurancePolicy.query.get(claim.policy_id)
            policy.status = 'CLAIMED'
            
            message = f"Claim approved for ₹{approved_amount}"
            
        elif decision == 'REJECTED':
            claim.status = 'REJECTED'
            claim.rejection_reason = rejection_reason
            claim.processed_at = datetime.utcnow()
            
            message = f"Claim rejected: {rejection_reason}"
        else:
            raise ValueError(f"Invalid decision: {decision}")
        
        db.session.commit()
        
        return {
            'claim_id': claim.id,
            'claim_number': claim.claim_number,
            'status': claim.status,
            'approved_amount': float(claim.approved_amount) if claim.approved_amount else None,
            'message': message
        }
    
    @staticmethod
    def mark_claim_paid(claim_id: int, payment_reference: str) -> Dict:
        """Mark a claim as paid (admin function)."""
        claim = ClaimRequest.query.get(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        
        if claim.status != 'APPROVED':
            raise ValueError(f"Cannot pay claim with status {claim.status}")
        
        claim.status = 'PAID'
        claim.payment_date = datetime.utcnow()
        claim.notes = f"Payment reference: {payment_reference}"
        
        db.session.commit()
        
        return {
            'claim_id': claim.id,
            'claim_number': claim.claim_number,
            'status': 'PAID',
            'paid_amount': float(claim.approved_amount),
            'payment_date': claim.payment_date.isoformat(),
            'message': 'Claim payment recorded successfully'
        }
    
    @staticmethod
    def get_insurance_statistics(user_id: Optional[int] = None) -> Dict:
        """
        Get insurance statistics (admin view or user view).
        
        Args:
            user_id: If provided, stats for specific user; otherwise, global stats
            
        Returns:
            dict: Statistics
        """
        if user_id:
            # User-specific stats
            policies_query = InsurancePolicy.query.filter_by(user_id=user_id)
            claims_query = ClaimRequest.query.filter_by(user_id=user_id)
        else:
            # Global stats
            policies_query = InsurancePolicy.query
            claims_query = ClaimRequest.query
        
        total_policies = policies_query.count()
        active_policies = policies_query.filter_by(status='ACTIVE').count()
        
        total_claims = claims_query.count()
        approved_claims = claims_query.filter_by(status='APPROVED').count()
        paid_claims = claims_query.filter_by(status='PAID').count()
        
        # Calculate total coverage and premiums
        total_coverage = db.session.query(
            func.sum(InsurancePolicy.coverage_amount)
        ).filter(
            InsurancePolicy.user_id == user_id if user_id else True
        ).scalar() or Decimal('0')
        
        total_premiums = db.session.query(
            func.sum(InsurancePolicy.premium_amount)
        ).filter(
            InsurancePolicy.user_id == user_id if user_id else True
        ).scalar() or Decimal('0')
        
        total_claims_amount = db.session.query(
            func.sum(ClaimRequest.approved_amount)
        ).filter(
            ClaimRequest.user_id == user_id if user_id else True,
            ClaimRequest.approved_amount.isnot(None)
        ).scalar() or Decimal('0')
        
        return {
            'total_policies': total_policies,
            'active_policies': active_policies,
            'total_claims': total_claims,
            'approved_claims': approved_claims,
            'paid_claims': paid_claims,
            'total_coverage': float(total_coverage),
            'total_premiums_collected': float(total_premiums),
            'total_claims_paid': float(total_claims_amount),
            'claim_ratio': (float(total_claims_amount) / float(total_premiums) * 100) if total_premiums > 0 else 0
        }
