from backend.models.processing import SpectralScanData, DynamicGradeAdjustment, ProcessingBatch
from backend.models.traceability import SupplyBatch, QualityGrade
from backend.models.market import ForwardContract
from backend.models.barter import ResourceValueIndex
from backend.models.procurement import BulkOrder
from backend.extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GradingEngine:
    """
    Autonomous Quality Assurance & Spectral Grading Engine (L3-1604).
    Implements Cascading Financial Recalculation across contracts and barter values.
    """

    @staticmethod
    def process_spectral_scan(batch_id, scan_data):
        """
        Parses raw chemical parameters to output a grade and financial multiplier.
        scan_data: {'moisture': 12.5, 'brix': 18.2, 'protein': 14.5}
        """
        batch = ProcessingBatch.query.get(batch_id)
        if not batch:
            return None, "Batch not found"

        # 1. Archive raw scan data
        scan = SpectralScanData(
            batch_id=batch_id,
            moisture_percentage=scan_data.get('moisture'),
            brix_level=scan_data.get('brix'),
            protein_percentage=scan_data.get('protein'),
            scan_integrity_score=0.98
        )
        db.session.add(scan)

        # 2. Logic to determine grade (Simplified)
        # Grade A: Protein > 13%, Brix > 15%, Moisture < 14%
        new_grade = 'B'
        penalty = 0.0
        
        if scan_data.get('protein', 0) > 13 and scan_data.get('brix', 0) > 15:
            new_grade = 'A'
        elif scan_data.get('moisture', 0) > 15:
            new_grade = 'C'
            penalty = 0.20 # 20% price drop

        # 3. Cascading Financial Recalculation (L3 Requirement)
        # This autonomously updates all linked financial instruments
        GradingEngine.trigger_cascading_updates(batch, new_grade, penalty)

        db.session.commit()
        return new_grade, penalty

    @staticmethod
    def trigger_cascading_updates(processing_batch, grade, penalty):
        """
        The core L3 complexity: Updates ForwardContracts, Barter values, and BulkOrders
        without user intervention.
        """
        logger.info(f"Cascading Quality Update for Batch {processing_batch.id} -> Grade {grade}")

        # A. Update associated SupplyBatches
        for supply_batch in processing_batch.supply_batches:
            old_grade = supply_batch.predicted_quality_grade
            supply_batch.predicted_quality_grade = grade
            
            # Log adjustment
            adjustment = DynamicGradeAdjustment(
                batch_id=processing_batch.id,
                old_grade=old_grade,
                new_grade=grade,
                price_penalty_factor=penalty,
                adjustment_reason=f"Spectral Scan: Protein {grade} threshold alignment"
            )
            db.session.add(adjustment)

            # B. Payout adjustment for Forward Contracts
            contract = ForwardContract.query.filter_by(batch_id=supply_batch.id).first()
            if contract:
                contract.quality_penalty_clause = penalty
                logger.info(f"Updated ForwardContract {contract.id} with {penalty*100}% quality penalty.")

            # C. Update Procurement Bulk Orders unit pricing
            orders = BulkOrder.query.filter_by(item_id=supply_batch.id).all() # Simplified link
            for order in orders:
                order.real_time_price_modifier = (1.0 - penalty)
                order.total_amount = order.quantity * order.unit_price * order.real_time_price_modifier

        # D. Update Barter Power (ResourceValueIndex)
        # Lowering the trade value of this specific crop type globally if 
        # this batch is representative of regional quality
        index_entry = ResourceValueIndex.query.filter_by(item_name=processing_batch.product_type).first()
        if index_entry and grade == 'C':
            index_entry.demand_multiplier *= 0.95 # 5% drop in barter power
            logger.info(f"Regional Barter Index for {processing_batch.product_type} adjusted due to low quality scans.")
        
        db.session.commit()
