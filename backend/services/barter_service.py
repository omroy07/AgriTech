from datetime import datetime
from backend.extensions import db
from backend.models.barter import BarterTransaction, BarterResource, BarterStatus, ResourceValueIndex
from backend.models.equipment import Equipment
from backend.models.labor import WorkerProfile
from backend.models.procurement import ProcurementItem
from backend.models.machinery import EngineHourLog
from backend.services.audit_service import AuditService
from backend.models.forum import UserReputation
import logging
import json

logger = logging.getLogger(__name__)

class ValueOrchestrator:
    """
    Orchestration Logic for calculating real-time exchange rates (Value-Index).
    Calculates the 'fair barter value' of resources.
    """
    
    @staticmethod
    def get_resource_value(category, ref_id, quantity):
        """Calculates the Value-Index for a specific resource."""
        base_val = 0.0
        details = {}
        
        # 1. Fetch System-wide Value Index Adjustment
        index_entry = ResourceValueIndex.query.filter_by(category=category, resource_id=ref_id if category != 'COMMODITY' else None).first()
        global_multiplier = index_entry.demand_multiplier if index_entry else 1.0

        if category == 'MACHINERY':
            equipment = Equipment.query.get(ref_id)
            if not equipment: return 0, {}
            # Base hourly rate
            base_val = equipment.hourly_rate
            # Apply Depreciation Factor based on total engine hours
            total_hours = db.session.query(db.func.sum(EngineHourLog.hours_end - EngineHourLog.hours_start)).filter_by(equipment_id=ref_id).scalar() or 0
            depreciation = min(0.3, (total_hours / 10000.0)) # Max 30% reduction for high-wear machines
            base_val *= (1 - depreciation)
            details['base_rate'] = equipment.hourly_rate
            details['depreciation'] = depreciation

        elif category == 'LABOR':
            profile = WorkerProfile.query.get(ref_id)
            if not profile: return 0, {}
            base_val = profile.base_hourly_rate
            details['base_rate'] = profile.base_hourly_rate

        elif category == 'COMMODITY' or category == 'SEEDS':
            item = ProcurementItem.query.get(ref_id)
            if not item: return 0, {}
            base_val = item.base_price
            details['base_price'] = item.base_price

        # Apply Global Demand Multiplier
        final_unit_value = base_val * global_multiplier
        total_value = final_unit_value * quantity
        
        details['global_multiplier'] = global_multiplier
        details['final_unit_value'] = final_unit_value
        
        return total_value, details

class BarterService:
    """
    Service for managing the Circular Economy Barter lifecycle.
    Implements Dual-Lock Escrow & Forensic Auditing.
    """

    @staticmethod
    def propose_barter(initiator_id, responder_id, offered_resources, requested_resources):
        """
        Creates a barter proposal with auto-balanced Value-Index.
        offered_resources: [{'category': 'MACHINERY', 'id': 1, 'qty': 5}, ...]
        """
        transaction = BarterTransaction(
            initiator_id=initiator_id,
            responder_id=responder_id,
            status=BarterStatus.PROPOSED
        )
        db.session.add(transaction)
        db.session.flush() # Get transaction ID

        # Process Offered Resources (from Initiator)
        for res in offered_resources:
            val, details = ValueOrchestrator.get_resource_value(res['category'], res['id'], res['qty'])
            resource = BarterResource(
                transaction_id=transaction.id,
                provider_id=initiator_id,
                resource_category=res['category'],
                resource_reference_id=res['id'],
                quantity=res['qty'],
                unit_value_index=val / res['qty'] if res['qty'] > 0 else 0,
                total_value_index=val
            )
            db.session.add(resource)

        # Process Requested Resources (from Responder)
        for res in requested_resources:
            val, details = ValueOrchestrator.get_resource_value(res['category'], res['id'], res['qty'])
            resource = BarterResource(
                transaction_id=transaction.id,
                provider_id=responder_id,
                resource_category=res['category'],
                resource_reference_id=res['id'],
                quantity=res['qty'],
                unit_value_index=val / res['qty'] if res['qty'] > 0 else 0,
                total_value_index=val
            )
            db.session.add(resource)

        db.session.commit()
        
        # Log to Forensic Barter Trail
        AuditService.log_event(
            user_id=initiator_id,
            action="BARTER_PROPOSED",
            resource_type="BARTER",
            resource_id=transaction.id,
            details=f"Proposed barter with User {responder_id}. Offered: {json.dumps(offered_resources)}",
            risk_level="LOW"
        )
        
        return transaction

    @staticmethod
    def lock_escrow(transaction_id, user_id):
        """
        Dual-Lock Escrow: Secures the resource commitment from one party.
        """
        tx = BarterTransaction.query.get(transaction_id)
        if not tx: return None
        
        if user_id == tx.initiator_id:
            tx.initiator_committed = True
        elif user_id == tx.responder_id:
            tx.responder_committed = True
            
        if tx.initiator_committed and tx.responder_committed:
            tx.status = BarterStatus.ESCROW_LOCKED
            # TODO: Add logic to "reserve" equipment/labor in their respective modules
        
        db.session.commit()
        
        AuditService.log_event(
            user_id=user_id,
            action="BARTER_ESCROW_LOCK",
            resource_type="BARTER",
            resource_id=tx.id,
            details=f"User {user_id} locked their side of the barter escrow.",
            risk_level="MEDIUM"
        )
        return tx

    @staticmethod
    def confirm_fulfillment(transaction_id, user_id):
        """Confirms that the physical resource or work was delivered."""
        tx = BarterTransaction.query.get(transaction_id)
        if not tx: return None
        
        if user_id == tx.initiator_id:
            tx.initiator_confirmed_fulfillment = True
        elif user_id == tx.responder_id:
            tx.responder_confirmed_fulfillment = True
            
        if tx.initiator_confirmed_fulfillment and tx.responder_confirmed_fulfillment:
            tx.status = BarterStatus.FULFILLED
            BarterService.finalize_barter(tx)
            
        db.session.commit()
        return tx

    @staticmethod
    def finalize_barter(tx):
        """Completes the circular exchange and updates reputations."""
        tx.status = BarterStatus.COMPLETED
        
        # Update Reputation for both farmers
        for user_id in [tx.initiator_id, tx.responder_id]:
            rep = UserReputation.query.filter_by(user_id=user_id).first()
            if not rep:
                rep = UserReputation(user_id=user_id, reputation_score=100)
                db.session.add(rep)
            rep.reputation_score += 10 # successful trade bonus
            
        AuditService.log_event(
            user_id=tx.initiator_id,
            action="BARTER_COMPLETED",
            resource_type="BARTER",
            resource_id=tx.id,
            details=f"Barter successfully finalized between {tx.initiator_id} and {tx.responder_id}.",
            risk_level="INFO"
        )
