"""
Farm-to-Fork Traceability & Dynamic QR Verification API Endpoints.
Location: backend/api/v1/traceability.py
"""

from flask import Blueprint, request, jsonify, Response, current_app
from backend.services.traceability_service import TraceabilityService
from backend.models.traceability import SupplyBatch, FarmLifecycleLog, BatchStatus
from backend.tasks.traceability_tasks import generate_batch_certificate_task
from backend.extensions import db
from auth_utils import token_required, roles_required
import logging

logger = logging.getLogger(__name__)
traceability_bp = Blueprint('traceability', __name__)


# ------------------------------------------------------------------------------
# 1. DYNAMIC QR CODE STICKER GENERATOR
# ------------------------------------------------------------------------------
@traceability_bp.route('/generate-qr/<batch_id>', methods=['GET'])
@traceability_bp.route('/qr/<batch_id>', methods=['GET'])
def generate_qr_sticker(batch_id):
    """
    Generate high-resolution printable packaging QR sticker image (PNG).
    """
    try:
        host_url = request.host_url
        qr_bytes = TraceabilityService.generate_qr_sticker_image(batch_id, host_url=host_url)
        return Response(qr_bytes, mimetype="image/png", headers={
            "Content-Disposition": f"inline; filename=QR_STICKER_{batch_id}.png"
        })
    except Exception as e:
        logger.error(f"Error generating QR sticker: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------------------------------------------------------------
# 2. CONSUMER BATCH PASSPORT & LIFECYCLE AUDIT TRAIL
# ------------------------------------------------------------------------------
@traceability_bp.route('/batches/<batch_id>', methods=['GET'])
@traceability_bp.route('/batch/<batch_id>', methods=['GET'])
def get_batch(batch_id):
    """
    Public endpoint to fetch full farm-to-fork batch lifecycle, farmer bio,
    carbon metrics, lab test reports, and cryptographic verification proof.
    """
    batch_data, error = TraceabilityService.get_batch_history(batch_id)
    if error:
        return jsonify({'status': 'error', 'message': error}), 404
    
    return jsonify({
        'status': 'success',
        'data': batch_data
    }), 200


# ------------------------------------------------------------------------------
# 3. CRYPTOGRAPHIC VERIFICATION ENDPOINT
# ------------------------------------------------------------------------------
@traceability_bp.route('/verify/<batch_id>', methods=['GET'])
def verify_batch_cryptography(batch_id):
    """
    Verify SHA-256 cryptographic chaining of all immutable farm lifecycle blocks.
    """
    is_valid, block_count = TraceabilityService.verify_batch_integrity(batch_id)
    batch_data, _ = TraceabilityService.get_batch_history(batch_id)

    return jsonify({
        "status": "success",
        "batch_id": batch_id,
        "is_cryptographically_valid": is_valid,
        "verified_blocks": block_count,
        "root_hash": batch_data.get("integrity_hash") if batch_data else None,
        "verification_timestamp": batch_data.get("updated_at") if batch_data else None,
        "message": "Immutable ledger audit trail verified successfully." if is_valid else "Ledger chain inconsistency detected."
    }), 200


# ------------------------------------------------------------------------------
# 4. LOG IMMUTABLE FARM LIFECYCLE EVENT
# ------------------------------------------------------------------------------
@traceability_bp.route('/log-event', methods=['POST'])
def log_lifecycle_event():
    """
    Append an immutable event (Seed, Soil Test, Bio-Pesticide, Irrigation, Harvest)
    into the farm activity ledger with SHA-256 cryptographic chaining.
    """
    data = request.get_json(silent=True) or {}
    batch_id = data.get('batch_id')
    event_type = data.get('event_type')
    event_title = data.get('event_title')

    if not batch_id or not event_type or not event_title:
        return jsonify({'status': 'error', 'message': 'batch_id, event_type, and event_title are required'}), 400

    batch = TraceabilityService.get_or_create_sample_batch(batch_id)
    last_log = batch.lifecycle_logs.order_by(FarmLifecycleLog.timestamp.desc()).first()
    prev_hash = last_log.block_hash if last_log else "GENESIS_BLOCK"

    new_event = FarmLifecycleLog.create_event(
        batch_id=batch.id,
        event_type=event_type,
        event_title=event_title,
        payload_data=data.get('payload', {}),
        previous_hash=prev_hash,
        performed_by=data.get('performed_by', 'Certified Agronomist'),
        location_name=data.get('location', batch.farm_location),
        notes=data.get('notes', ''),
        carbon_impact_kg=float(data.get('carbon_impact_kg', 0.0))
    )
    db.session.add(new_event)
    batch.integrity_hash = new_event.block_hash
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Immutable lifecycle event recorded.',
        'event': new_event.to_dict()
    }), 201


# ------------------------------------------------------------------------------
# 5. CREATE BATCH
# ------------------------------------------------------------------------------
@traceability_bp.route('/batches', methods=['POST'])
@traceability_bp.route('/create-batch', methods=['POST'])
def create_batch():
    """Create a new produce batch starting at the farm"""
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    required = ['crop_name', 'quantity', 'farm_location']
    if not all(k in data for k in required):
        return jsonify({'status': 'error', 'message': f'Missing required fields: {required}'}), 400
    
    farmer_id = data.get('farmer_id', 1)
    batch_id = f"AGRI-{data['crop_name'][:3].upper()}-{data.get('quantity')}-{uuid.uuid4().hex[:6].upper()}"
    
    batch = TraceabilityService.get_or_create_sample_batch(batch_id)
    
    return jsonify({
        'status': 'success',
        'data': batch.to_dict(),
        'qr_sticker_url': f"/api/v1/traceability/generate-qr/{batch.batch_internal_id}",
        'message': 'Batch created and immutable genesis block initialized.'
    }), 201
