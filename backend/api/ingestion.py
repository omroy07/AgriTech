from flask import Blueprint, request, jsonify
from backend.services.pipeline_service import MediaPipelineService
from auth_utils import token_required
import json

ingestion_bp = Blueprint('ingestion', __name__)

@ingestion_bp.route('/ingest/upload', methods=['POST'])
@token_required
def upload_media():
    """
    Standardized endpoint for all media and data file uploads.
    Supports DISEASE, SOIL, CROP, EQUIPMENT types.
    """
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
    file = request.files['file']
    payload_type = request.form.get('type')
    metadata_raw = request.form.get('metadata', '{}')
    
    if not payload_type:
        return jsonify({'status': 'error', 'message': 'Payload type is required'}), 400
        
    try:
        metadata = json.loads(metadata_raw)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Invalid metadata JSON'}), 400
        
    user_id = request.user.get('id') or request.user.get('user_id')
    
    payload, error = MediaPipelineService.ingest_payload(
        file, 
        payload_type.upper(), 
        user_id=user_id, 
        metadata=metadata
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'message': 'Payload ingested and processing started',
        'tracking_id': payload.tracking_id
    }), 202

@ingestion_bp.route('/ingest/status/<tracking_id>', methods=['GET'])
@token_required
def get_status(tracking_id):
    """Check the status of a specific processing tracking ID."""
    payload = MediaPipelineService.get_payload_status(tracking_id)
    if not payload:
        return jsonify({'status': 'error', 'message': 'Invalid tracking ID'}), 404
        
    return jsonify({
        'status': 'success',
        'data': payload.to_dict()
    }), 200
