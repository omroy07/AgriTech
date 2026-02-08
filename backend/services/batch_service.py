"""
Batch Service for Supply Chain Traceability
Implements state-machine based lifecycle management for produce batches
"""

from datetime import datetime
from flask import request
import json
import uuid
import hashlib

from backend.extensions import db
from backend.models import ProduceBatch, AuditTrail, BatchStatus, User, UserRole
from backend.utils.qr_generator import get_qr_generator
from security_utils import log_security_event


class BatchService:
    """
    Service layer for managing produce batch lifecycle.
    Handles state transitions, audit logging, and QR code generation.
    """
    
    @staticmethod
    def create_batch(user_id, produce_name, produce_type, quantity_kg, 
                     origin_location, harvest_date=None, certification=None,
                     quality_grade=None, quality_notes=None):
        """
        Create a new produce batch (Farmer only).
        
        Args:
            user_id: ID of the farmer creating the batch
            produce_name: Name of the produce
            produce_type: Type of produce (vegetable, fruit, grain, etc.)
            quantity_kg: Quantity in kilograms
            origin_location: Farm/origin location
            harvest_date: Date of harvest (defaults to now)
            certification: Optional certification (organic, non-GMO, etc.)
            quality_grade: Optional initial quality grade
            quality_notes: Optional quality notes
            
        Returns:
            tuple: (ProduceBatch object, error_message)
        """
        try:
            # Verify user is a farmer
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            
            if user.role != UserRole.FARMER:
                log_security_event('UNAUTHORIZED_BATCH_CREATE', 
                                 f'User {user.email} (role: {user.role}) attempted to create batch')
                return None, "Only farmers can create produce batches"
            
            # Generate unique batch ID
            batch_id = BatchService._generate_batch_id(user_id, produce_name)
            
            # Generate QR code
            qr_generator = get_qr_generator()
            harvest_dt = harvest_date or datetime.utcnow()
            
            qr_image, encrypted_data = qr_generator.generate_batch_qr(
                batch_id=batch_id,
                produce_name=produce_name,
                harvest_date=harvest_dt,
                farmer_id=user_id,
                origin_location=origin_location,
                additional_data={
                    'produce_type': produce_type,
                    'certification': certification
                }
            )
            
            # Create batch record
            batch = ProduceBatch(
                batch_id=batch_id,
                qr_code=encrypted_data,
                produce_name=produce_name,
                produce_type=produce_type,
                quantity_kg=quantity_kg,
                origin_location=origin_location,
                status=BatchStatus.HARVESTED,
                farmer_id=user_id,
                current_handler_id=user_id,
                harvest_date=harvest_dt,
                certification=certification,
                quality_grade=quality_grade,
                quality_notes=quality_notes
            )
            
            db.session.add(batch)
            db.session.flush()  # Get batch.id before creating audit log
            
            # Create initial audit log
            BatchService._create_audit_log(
                batch_id=batch.id,
                event_type='BATCH_CREATED',
                from_status=None,
                to_status=BatchStatus.HARVESTED,
                user_id=user_id,
                user_role=user.role,
                user_email=user.email,
                notes=f'Batch created: {produce_name} ({quantity_kg}kg) from {origin_location}'
            )
            
            db.session.commit()
            
            log_security_event('BATCH_CREATED', f'Batch {batch_id} created by farmer {user.email}')
            
            return batch, None
        
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating batch: {str(e)}"
    
    @staticmethod
    def transition_batch_status(batch_id, new_status, user_id, notes=None, 
                                location=None, quality_grade=None, quality_notes=None):
        """
        Transition batch to new status with role-based access control.
        
        Args:
            batch_id: ID of the batch
            new_status: Target status
            user_id: ID of user performing transition
            notes: Optional notes about the transition
            location: Optional location information
            quality_grade: Optional quality grade update
            quality_notes: Optional quality notes
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            batch = ProduceBatch.query.filter_by(batch_id=batch_id).first()
            if not batch:
                return False, "Batch not found"
            
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Validate status
            if not BatchStatus.is_valid(new_status):
                return False, f"Invalid status: {new_status}"
            
            # Check if transition is allowed
            if not batch.can_transition_to(new_status, user.role):
                log_security_event('UNAUTHORIZED_STATUS_CHANGE',
                                 f'User {user.email} (role: {user.role}) attempted to change batch {batch_id} from {batch.status} to {new_status}')
                return False, f"User role '{user.role}' cannot transition batch from '{batch.status}' to '{new_status}'"
            
            # Store old status
            old_status = batch.status
            
            # Update batch status
            batch.status = new_status
            batch.current_handler_id = user_id
            batch.updated_at = datetime.utcnow()
            
            # Update status-specific timestamps
            if new_status == BatchStatus.QUALITY_CHECK:
                batch.quality_check_date = datetime.utcnow()
            elif new_status == BatchStatus.LOGISTICS:
                batch.logistics_date = datetime.utcnow()
            elif new_status == BatchStatus.IN_SHOP:
                batch.received_date = datetime.utcnow()
                batch.shopkeeper_id = user_id
            
            # Update quality information if provided
            if quality_grade:
                batch.quality_grade = quality_grade
            if quality_notes:
                batch.quality_notes = quality_notes
            
            # Create audit log
            BatchService._create_audit_log(
                batch_id=batch.id,
                event_type='STATUS_CHANGE',
                from_status=old_status,
                to_status=new_status,
                user_id=user_id,
                user_role=user.role,
                user_email=user.email,
                notes=notes,
                location=location,
                metadata=json.dumps({
                    'quality_grade': quality_grade,
                    'quality_notes': quality_notes
                }) if quality_grade or quality_notes else None
            )
            
            db.session.commit()
            
            log_security_event('BATCH_STATUS_CHANGED',
                             f'Batch {batch_id} changed from {old_status} to {new_status} by {user.email}')
            
            return True, f"Batch status updated to {new_status}"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating batch status: {str(e)}"
    
    @staticmethod
    def update_quality_info(batch_id, quality_grade, quality_notes, user_id):
        """
        Update quality information for a batch.
        
        Args:
            batch_id: ID of the batch
            quality_grade: Quality grade (A, B, C)
            quality_notes: Notes about quality
            user_id: ID of user performing update
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            batch = ProduceBatch.query.filter_by(batch_id=batch_id).first()
            if not batch:
                return False, "Batch not found"
            
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Only farmers and admins can update quality
            if user.role not in [UserRole.FARMER, UserRole.ADMIN]:
                return False, "Insufficient permissions to update quality information"
            
            batch.quality_grade = quality_grade
            batch.quality_notes = quality_notes
            batch.updated_at = datetime.utcnow()
            
            # Create audit log
            BatchService._create_audit_log(
                batch_id=batch.id,
                event_type='QUALITY_UPDATE',
                from_status=batch.status,
                to_status=batch.status,
                user_id=user_id,
                user_role=user.role,
                user_email=user.email,
                notes=f'Quality updated: Grade {quality_grade}',
                metadata=json.dumps({
                    'quality_grade': quality_grade,
                    'quality_notes': quality_notes
                })
            )
            
            db.session.commit()
            
            return True, "Quality information updated successfully"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating quality: {str(e)}"
    
    @staticmethod
    def get_batch_by_id(batch_id, include_audit=False):
        """
        Retrieve batch by batch_id.
        
        Args:
            batch_id: Unique batch identifier
            include_audit: Whether to include audit trail
            
        Returns:
            ProduceBatch object or None
        """
        batch = ProduceBatch.query.filter_by(batch_id=batch_id).first()
        if batch and include_audit:
            # Ensure audit logs are loaded
            batch.audit_logs.all()
        return batch
    
    @staticmethod
    def get_batches_by_farmer(farmer_id, status=None):
        """
        Get all batches created by a farmer.
        
        Args:
            farmer_id: ID of the farmer
            status: Optional status filter
            
        Returns:
            List of ProduceBatch objects
        """
        query = ProduceBatch.query.filter_by(farmer_id=farmer_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(ProduceBatch.created_at.desc()).all()
    
    @staticmethod
    def get_batches_by_shopkeeper(shopkeeper_id, status=None):
        """
        Get all batches received by a shopkeeper.
        
        Args:
            shopkeeper_id: ID of the shopkeeper
            status: Optional status filter
            
        Returns:
            List of ProduceBatch objects
        """
        query = ProduceBatch.query.filter_by(shopkeeper_id=shopkeeper_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(ProduceBatch.received_date.desc()).all()
    
    @staticmethod
    def get_batches_by_status(status):
        """
        Get all batches with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of ProduceBatch objects
        """
        return ProduceBatch.query.filter_by(status=status).order_by(ProduceBatch.updated_at.desc()).all()
    
    @staticmethod
    def verify_qr_code(encrypted_data):
        """
        Verify and decode QR code data.
        
        Args:
            encrypted_data: Encrypted data from QR code
            
        Returns:
            tuple: (decoded_data dict or None, error_message)
        """
        qr_generator = get_qr_generator()
        decoded_data = qr_generator.verify_and_decode_qr(encrypted_data)
        
        if not decoded_data:
            return None, "Invalid or tampered QR code"
        
        return decoded_data, None
    
    @staticmethod
    def get_traceability_passport(batch_id):
        """
        Generate complete traceability passport for public verification.
        
        Args:
            batch_id: Unique batch identifier
            
        Returns:
            dict: Traceability passport or None
        """
        batch = BatchService.get_batch_by_id(batch_id, include_audit=True)
        if not batch:
            return None
        
        # Get audit logs
        audit_logs = [log.to_dict() for log in batch.audit_logs.order_by(AuditTrail.timestamp.asc()).all()]
        
        # Generate passport
        qr_generator = get_qr_generator()
        passport = qr_generator.create_traceability_passport(
            batch_data=batch.to_dict(),
            audit_logs=audit_logs
        )
        
        return passport
    
    @staticmethod
    def _generate_batch_id(user_id, produce_name):
        """
        Generate unique batch ID.
        
        Args:
            user_id: Farmer ID
            produce_name: Name of produce
            
        Returns:
            str: Unique batch ID
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_str = f"{user_id}-{produce_name}-{timestamp}-{uuid.uuid4().hex[:8]}"
        hash_obj = hashlib.sha256(unique_str.encode())
        return f"BATCH-{hash_obj.hexdigest()[:16].upper()}"
    
    @staticmethod
    def _create_audit_log(batch_id, event_type, from_status, to_status, 
                         user_id, user_role, user_email, notes=None, 
                         location=None, metadata=None):
        """
        Create immutable audit log entry.
        
        Args:
            batch_id: ID of the batch
            event_type: Type of event
            from_status: Previous status
            to_status: New status
            user_id: ID of user performing action
            user_role: Role of user
            user_email: Email of user
            notes: Optional notes
            location: Optional location
            metadata: Optional metadata JSON string
        """
        ip_address = request.remote_addr if request else None
        
        audit_log = AuditTrail(
            batch_id=batch_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            user_id=user_id,
            user_role=user_role,
            user_email=user_email,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            location=location,
            notes=notes,
            event_metadata=metadata
        )
        
        # Generate signature for tamper detection
        signature_data = f"{batch_id}-{event_type}-{from_status}-{to_status}-{user_id}-{audit_log.timestamp.isoformat()}"
        audit_log.signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        db.session.add(audit_log)
