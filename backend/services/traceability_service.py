import uuid
from datetime import datetime
from backend.extensions import db
from backend.models.traceability import SupplyBatch, CustodyLog, QualityGrade, BatchStatus
from backend.utils.qr_generator import QRGenerator
import json

class TraceabilityService:
    @staticmethod
    def create_batch(farmer_id, crop_name, quantity, farm_location, crop_variety=None, unit='KG'):
        """Create a new produce batch starting at the farm"""
        try:
            batch_id = f"AGRI-{uuid.uuid4().hex[:8].upper()}-{datetime.now().strftime('%y%m%d')}"
            
            # Generate QR Code
            qr_data = QRGenerator.generate_batch_qr(batch_id)
            
            batch = SupplyBatch(
                batch_internal_id=batch_id,
                farmer_id=farmer_id,
                current_handler_id=farmer_id,
                crop_name=crop_name,
                crop_variety=crop_variety,
                quantity=quantity,
                unit=unit,
                farm_location=farm_location,
                qr_code_data=qr_data,
                status=BatchStatus.HARVESTED
            )
            
            db.session.add(batch)
            db.session.flush()
            
            # Log the initial action
            log = CustodyLog(
                batch_id=batch.id,
                handler_id=farmer_id,
                action='HARVESTED',
                to_status=BatchStatus.HARVESTED,
                location=farm_location,
                notes="Initial harvest and batch creation."
            )
            db.session.add(log)
            
            batch.integrity_hash = batch.generate_integrity_hash()
            db.session.commit()
            
            return batch, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def add_quality_check(batch_id, inspector_id, grade, parameters, notes=None):
        """Add a quality inspection record to the batch"""
        try:
            batch = SupplyBatch.query.filter_by(batch_internal_id=batch_id).first()
            if not batch:
                return None, "Batch not found"
            
            quality = QualityGrade(
                batch_id=batch.id,
                inspector_id=inspector_id,
                grade=grade,
                parameters=json.dumps(parameters),
                notes=notes
            )
            db.session.add(quality)
            
            # Transition status
            old_status = batch.status
            if grade in ['A', 'B', 'Premium']:
                batch.status = BatchStatus.QUALITY_CHECK
            else:
                batch.status = BatchStatus.REJECTED
            
            log = CustodyLog(
                batch_id=batch.id,
                handler_id=inspector_id,
                action='QUALITY_INSPECTION',
                from_status=old_status,
                to_status=batch.status,
                notes=f"Quality check completed. Grade: {grade}"
            )
            db.session.add(log)
            
            batch.integrity_hash = batch.generate_integrity_hash()
            db.session.commit()
            
            return batch, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def transfer_custody(batch_id, current_handler_id, new_handler_id, new_status, location, notes=None):
        """Record a transfer of custody from one handler to another"""
        try:
            batch = SupplyBatch.query.filter_by(batch_internal_id=batch_id).first()
            if not batch:
                return None, "Batch not found"
            
            if batch.current_handler_id != current_handler_id:
                return None, "Unauthorized: Only current handler can initiate transfer"
            
            old_status = batch.status
            batch.current_handler_id = new_handler_id
            batch.status = new_status
            
            log = CustodyLog(
                batch_id=batch.id,
                handler_id=new_handler_id,
                action='CUSTODY_TRANSFER',
                from_status=old_status,
                to_status=new_status,
                location=location,
                notes=notes
            )
            db.session.add(log)
            
            batch.integrity_hash = batch.generate_integrity_hash()
            db.session.commit()
            
            return batch, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_batch_history(batch_id):
        """Retrieve full audit trail and current status"""
        batch = SupplyBatch.query.filter_by(batch_internal_id=batch_id).first()
        if not batch:
            return None, "Batch not found"
        return batch.to_dict(include_logs=True), None
