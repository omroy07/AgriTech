from datetime import datetime
from backend.extensions import db
from backend.models.processing import ProcessingBatch, StageLog, QualityCheck, ProcessingStage
from backend.utils.quality_formulas import QualityFormulas
import uuid
import logging

logger = logging.getLogger(__name__)

class ProcessingService:
    @staticmethod
    def create_batch(product_type, weight, origin_farms):
        """Initialize a new raw material batch"""
        try:
            batch = ProcessingBatch(
                batch_number=f"BAT-{uuid.uuid4().hex[:8].upper()}",
                product_type=product_type,
                total_weight=weight,
                current_weight=weight,
                origin_farms=origin_farms
            )
            db.session.add(batch)
            db.session.flush()
            
            # Log initial stage
            log = StageLog(
                batch_id=batch.id,
                stage_name=ProcessingStage.COLLECTION.value,
                notes="Batch consolidated from origin farms"
            )
            db.session.add(log)
            db.session.commit()
            return batch, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def perform_audit(batch_id, auditor_id, moisture, purity, weight):
        """Conduct a mandatory QA audit for the current stage"""
        batch = ProcessingBatch.query.get(batch_id)
        if not batch:
            return None, "Batch not found"
            
        # Scientific validation
        moisture_ok = QualityFormulas.is_moisture_acceptable(batch.product_type, moisture)
        purity_ok = purity >= 90.0 # Standard threshold
        
        is_passed = moisture_ok and purity_ok
        
        audit = QualityCheck(
            batch_id=batch_id,
            stage_name=batch.current_stage,
            moisture_content=moisture,
            purity_level=purity,
            weight_recorded=weight,
            is_passed=is_passed,
            auditor_id=auditor_id,
            comments=f"Audit for {batch.current_stage} stage. {'PASS' if is_passed else 'FAIL'}"
        )
        
        # Update batch weight if recorded
        batch.current_weight = weight
        db.session.add(audit)
        db.session.commit()
        return audit, None

    @staticmethod
    def advance_stage(batch_id, operator_id, next_stage):
        """Transition batch to the next stage if QA passed"""
        batch = ProcessingBatch.query.get(batch_id)
        if not batch:
            return False, "Batch not found"
            
        # 1. Verification: At least one passed QA check for current stage
        last_check = QualityCheck.query.filter_by(batch_id=batch_id, stage_name=batch.current_stage)\
            .order_by(QualityCheck.timestamp.desc()).first()
            
        if not last_check or not last_check.is_passed:
            return False, f"Mandatory QA audit for {batch.current_stage} failed or missing"
            
        # 2. Transition State
        old_stage = batch.current_stage
        batch.current_stage = next_stage
        
        if next_stage == ProcessingStage.COMPLETED.value:
            batch.completed_at = datetime.utcnow()
            
        # Log transition
        log = StageLog(
            batch_id=batch.id,
            stage_name=next_stage,
            operator_id=operator_id,
            notes=f"Moved from {old_stage} to {next_stage}"
        )
        db.session.add(log)
        db.session.commit()
        return True, None

    @staticmethod
    def get_batch_genealogy(batch_id):
        """Get full history of stages and audits for a batch"""
        batch = ProcessingBatch.query.get(batch_id)
        if not batch:
            return None
            
        stages = StageLog.query.filter_by(batch_id=batch_id).order_by(StageLog.started_at.asc()).all()
        audits = QualityCheck.query.filter_by(batch_id=batch_id).order_by(QualityCheck.timestamp.asc()).all()
        
        return {
            'batch': batch.to_dict(),
            'lifecycle': [
                {
                    'stage': s.stage_name, 
                    'time': s.started_at.isoformat(),
                    'notes': s.notes
                } for s in stages
            ],
            'audits': [a.to_dict() for a in audits]
        }
