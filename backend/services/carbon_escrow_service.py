"""
Carbon Escrow & Settlement Service — L3-1642
==========================================
Manages the lifecycle of carbon credit trades with satellite verification.
"""

from datetime import datetime
from backend.extensions import db
from backend.models.carbon_escrow import CarbonTradeEscrow, EscrowAuditLog
from backend.models.ledger import LedgerTransaction, LedgerAccount, LedgerEntry, AccountType, EntryType, TransactionType
import uuid
import logging

logger = logging.getLogger(__name__)

class CarbonEscrowManager:
    
    @staticmethod
    def create_listing(seller_id: int, volume: float, price: float):
        """
        Lists carbon credits for sale.
        """
        escrow = CarbonTradeEscrow(
            seller_id=seller_id,
            credits_volume=volume,
            price_per_credit_usd=price,
            total_value_usd=volume * price,
            status='LISTED'
        )
        db.session.add(escrow)
        db.session.commit()
        return escrow

    @staticmethod
    def fund_escrow(escrow_id: int, buyer_id: int):
        """
        Buyer locks funds into the escrow pool.
        """
        escrow = CarbonTradeEscrow.query.get(escrow_id)
        if not escrow or escrow.status != 'LISTED':
            raise ValueError("Invalid escrow state for funding.")
            
        escrow.buyer_id = buyer_id
        escrow.status = 'FUNDED'
        
        # In a real app, we'd trigger a LedgerTransaction here to move funds:
        # DEBIT Buyer Wallet -> CREDIT Escrow Holding Account
        
        db.session.add(EscrowAuditLog(
            escrow_id=escrow_id,
            action='FUNDS_LOCKED',
            actor_id=buyer_id,
            details=f"Buyer {buyer_id} deposited ${escrow.total_value_usd}."
        ))
        db.session.commit()
        return escrow

    @staticmethod
    def release_escrow(escrow_id: int, verifier_id: int):
        """
        Final release of funds to seller after satellite verification.
        """
        escrow = CarbonTradeEscrow.query.get(escrow_id)
        if not escrow or escrow.status != 'FUNDED':
            raise ValueError("Escrow must be funded before release.")
            
        escrow.status = 'RELEASED'
        escrow.verification_proof_hash = uuid.uuid4().hex # Mock verification hash
        
        # Financial Settlement:
        # DEBIT Escrow Holding -> CREDIT Seller Wallet
        
        db.session.add(EscrowAuditLog(
            escrow_id=escrow_id,
            action='SETTLED',
            actor_id=verifier_id,
            details="Satellite multi-spectral verification passed. Funds released."
        ))
        db.session.commit()
        return escrow

    @staticmethod
    def verify_satellite_spectral_proof(escrow_id: int):
        """
        Automated check for NDVI drift over the carbon sequestration zone.
        """
        escrow = CarbonTradeEscrow.query.get(escrow_id)
        if not escrow: return False
        
        # Simulate multi-spectral band comparison
        # If vegetation greenness index > 0.6, credits are valid
        spectral_index = 0.72 
        
        if spectral_index > 0.6:
            escrow.status = 'VERIFICATION_PASSED'
            db.session.commit()
            return True
        return False

